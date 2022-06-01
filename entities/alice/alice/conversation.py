def get_from_env(key: str) -> str:
    return os.environ[key]


@config
class StaticConfig:
    static: Any


@op(config_class=StaticConfig,)
def return_static_config(self) -> Any:
    return self.config.static


def static_config(
    call_this_to_create_object: Callable[[], Any], *args, **kwargs
) -> Callable[
    [],
]:
    return op(
        *args,
        config_cls=replace_config(
            "StaticlyDefinedConfig",
            return_static_config.imp.CONFIG,
            {"static": {"default_factory": static}},
        ),
        **kwargs,
    )(return_static_config)


@op(Example=static_config(BaseDataFlowFacilitatorObject),)
async def double_context_entry(
    dffml_plugin: BaseDataFlowFacilitatorObject,
) -> BaseDataFlowFacilitatorObjectContext:
    async with dffml_plugin as entered_dffml_plugin:
        async with entered_dffml_plugin() as ctx:
            yield ctx


@op(Example=GetConfigExample,)
def get_config(kvstore_ctx: BaseKeyValueStoreContext, key: str) -> Any:
    return kvstore_ctx.get(key)


Entity = NewType("Entity", str)


@op(
    # async lambda self: get_from_env(await self.octx.get_config(self.config.user_var_within_env)),
)
def get_from_env_entity() -> str:
    return os.environ[key]


@op(
    # Within parent system context, if VarsFromEnv exists as a
    # definition (TODO: DIDs for definitions, should get for
    # free if we switch to linage / locality via Inputs and
    # defintions via Input parents
    VarsFromEnv=get_from_env_entity,
)
def say_hello(entity: Entity) -> str:
    return f"Hello {entity}"


async def main():
    async with sysctx() as ctx:
        # Get the default output for a system context
        result = await ctx()
        # Run specific overlay for output method on system context
        principles = await ctx.strategic_principles()

        # Example with speaking to Alice
        OurEntitiesName = NewType(OurEntitiesName, Entity)

        def decide_if_a_response_is_needed_to_a_phrase_heard(
            self, phrase: PhraseHeard, our_entities_name: OurEntitiesName = "Alice",
        ) -> None:
            # Split the incoming phrase
            phrase_split = phrase.lower().split()
            if not phrase_split:
                return
            # Check we we're being addressed
            return phrase_split[0].startswith(our_entities_name.lower())

        # Source of phrases is just Record.keys
        PhraseSource = NewType(OurEntitiesName, BaseSource)

        @op
        def example_phrase_source() -> PhraseSource:
            return MemorySource(records=[Record("Alice what's up"),],)

        @op(
            # We were playing with syntax
            # Example: {
            #     example_phrase_source,
            # },
        )
        async def listen_for_phrases(phrase_source: PhraseSource) -> PhraseHeard:
            async for phrase in load(phrase_source):
                yield phrase.key

        @op(
            decide_if_a_response_is_needed_to_a_phrase_heard, listen_for_phrases,
        )
        async def phrase_heard_set_trigger_for_response_if_needed(
            # : PhraseHeard,
        ) -> None:
            pass
