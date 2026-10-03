from query_layer.providers.ollama_provider import plan_question
from query_layer.service import ask_census


def assert_equal(actual, expected, message):
    if actual != expected:
        raise AssertionError(
            f"{message}\n"
            f"Expected: {expected}\n"
            f"Actual:   {actual}"
        )


print("1. Difference comparison planning")

plan = plan_question(
    "How much larger is Punjab's male population "
    "than its female population?"
)

if plan.query is None:
    raise AssertionError("Planner returned no query.")

assert_equal(
    plan.query.comparison.operation,
    "difference",
    "Difference operation was not inferred.",
)

assert_equal(
    plan.query.comparison.left_metric,
    "male_population",
    "Wrong left comparison metric.",
)

assert_equal(
    plan.query.comparison.right_metric,
    "female_population",
    "Wrong right comparison metric.",
)

print("PASS")


print("2. Punjab male-female difference")

_, _, answer = ask_census(
    "How much larger is Punjab's male population "
    "than its female population?"
)

if answer is None:
    raise AssertionError("No answer returned.")

if "3,236,098" not in answer.answer:
    raise AssertionError(
        f"Expected difference not found:\n{answer.answer}"
    )

print("PASS")


print("3. Percentage comparison planning")

plan = plan_question(
    "What percentage higher is Sindh's urban population "
    "than its rural population?"
)

if plan.query is None:
    raise AssertionError("Planner returned no query.")

assert_equal(
    plan.query.comparison.operation,
    "percent_change",
    "Percentage operation was not inferred.",
)

assert_equal(
    plan.query.comparison.left_metric,
    "urban_population",
    "Wrong left percentage metric.",
)

assert_equal(
    plan.query.comparison.right_metric,
    "rural_population",
    "Wrong right percentage metric.",
)

print("PASS")


print("4. Generic compare does not invent arithmetic")

plan = plan_question(
    "Compare rural and urban population across provinces."
)

if plan.query is None:
    raise AssertionError("Planner returned no query.")

assert_equal(
    plan.query.comparison,
    None,
    "Generic comparison incorrectly added arithmetic.",
)

print("PASS")

print("\nComparison regression tests passed.")