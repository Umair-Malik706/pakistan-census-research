import time

from query_layer.answerer import generate_answer
from query_layer.executor import execute_query
from query_layer.interpreter import interpret_query
from query_layer.models import (
    CensusAnswer,
    PlannerResponse,
    QueryInterpretation,
    QueryResult,
    QueryTimings,
)
from query_layer.providers.ollama_provider import plan_question
from query_layer.renderer import render_simple_answer


def _ask_census_core(
    question: str,
    show_timings: bool = False,
) -> tuple[
    PlannerResponse,
    QueryResult | None,
    CensusAnswer | None,
    QueryInterpretation | None,
    QueryTimings,
]:
    total_started = time.perf_counter()

    planner_started = time.perf_counter()
    plan = plan_question(question)
    planner_seconds = time.perf_counter() - planner_started

    if plan.status == "unsupported":
        total_seconds = time.perf_counter() - total_started

        timings = QueryTimings(
            planner_seconds=planner_seconds,
            query_seconds=None,
            answer_seconds=None,
            total_seconds=total_seconds,
        )

        if show_timings:
            print(f"Planner: {planner_seconds:.2f}s")
            print(f"Total:   {total_seconds:.2f}s")

        return plan, None, None, None, timings

    if plan.query is None:
        raise RuntimeError(
            "Planner returned a ready response without a query."
        )

    interpretation = interpret_query(plan.query)

    query_started = time.perf_counter()
    result = execute_query(plan.query)
    query_seconds = time.perf_counter() - query_started

    answer_started = time.perf_counter()

    answer = render_simple_answer(
        question=question,
        result=result,
    )

    if answer is None:
        answer = generate_answer(
            question=question,
            result=result,
        )

    answer_seconds = time.perf_counter() - answer_started
    total_seconds = time.perf_counter() - total_started

    timings = QueryTimings(
        planner_seconds=planner_seconds,
        query_seconds=query_seconds,
        answer_seconds=answer_seconds,
        total_seconds=total_seconds,
    )

    if show_timings:
        print(f"Planner: {planner_seconds:.2f}s")
        print(f"Query:   {query_seconds:.2f}s")
        print(f"Answer:  {answer_seconds:.2f}s")
        print(f"Total:   {total_seconds:.2f}s")

    return plan, result, answer, interpretation, timings


def ask_census(
    question: str,
    show_timings: bool = False,
) -> tuple[
    PlannerResponse,
    QueryResult | None,
    CensusAnswer | None,
]:
    (
        plan,
        result,
        answer,
        _interpretation,
        _timings,
    ) = _ask_census_core(
        question,
        show_timings=show_timings,
    )

    return plan, result, answer


def ask_census_with_metadata(
    question: str,
    show_timings: bool = False,
) -> tuple[
    PlannerResponse,
    QueryResult | None,
    CensusAnswer | None,
    QueryInterpretation | None,
    QueryTimings,
]:
    return _ask_census_core(
        question,
        show_timings=show_timings,
    )