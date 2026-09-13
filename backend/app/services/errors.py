"""
Custom exceptions for the triage pipeline.
"""


class TriagePipelineError(Exception):
    """
    Raised for expected failures in the triage pipeline (e.g. the LLM
    provider errored or returned output that could not be parsed/validated).
    Callers should catch this and fall back to the safe default response,
    as distinct from an unexpected code defect (bare Exception).
    """
    pass
