from pydantic import AliasGenerator, BaseModel, ConfigDict, alias_generators


class CamelCaseModel(BaseModel):
    """Serialize model fields with camel-case aliases."""

    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=alias_generators.to_camel,
            serialization_alias=alias_generators.to_camel,
        ),
        validate_by_name=True,
        validate_by_alias=True,
        from_attributes=True,
    )
