"""Enrichment stages — company/domain/email/tech. AI via ports only."""
from __future__ import annotations

from signalhub.core.contracts.pipeline import PipelineContext, PipelineStage


class CompanyResolverStage(PipelineStage):
    name = "company_resolver"

    def process(self, ctx: PipelineContext) -> PipelineContext:
        # Wired later — pass-through without inventing companies.
        return ctx


class DomainResolverStage(PipelineStage):
    name = "domain_resolver"

    def process(self, ctx: PipelineContext) -> PipelineContext:
        return ctx


class EmailValidatorStage(PipelineStage):
    name = "email_validator"

    def process(self, ctx: PipelineContext) -> PipelineContext:
        return ctx


class TechStackDetectorStage(PipelineStage):
    name = "tech_stack_detector"

    def process(self, ctx: PipelineContext) -> PipelineContext:
        return ctx
