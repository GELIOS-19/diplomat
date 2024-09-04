from pathlib import Path

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import openai

from .snapshot import query_snapshot_space

from apps.users.models import Profile

try:
    openai.api_key = settings.LARGE_LANGUAGE_MODEL_PROVIDERS["openai"]["key"]
except (KeyError, AttributeError):
    raise ImproperlyConfigured(
        "Either the `LARGE_LANGUAGE_MODEL_PROVIDERS` setting is missing or it"
        " is improperly configured"
    )


class CompletionRequest:
    """
    A class to represent the necessary information to construct a
    prompt for querying a Language Model (LLM).

    Attributes
    ----------
    large_language_model : Profile.LargeLanguageModelChoices
        The large language model choice associated with the request.

    Methods
    -------
    about_statement() -> str
        Returns a statement about the organization.
    proposal_statement() -> str
        Returns the proposal title and body.
    personal_statement() -> str
        Returns a statement with the user's personal information.
    """

    large_language_model: Profile.LargeLanguageModelChoices

    def __init__(self, profile: Profile, proposal: dict):
        self._profile = profile
        self._proposal = proposal
        self.large_language_model = profile.large_language_model

    @property
    def about_statement(self) -> str:
        space = query_snapshot_space(self._proposal["space"]["id"])["spaces"][0]
        space_about = space["about"]
        if space_about:
            return f"The point of the organization is {space_about}"
        return ""

    @property
    def proposal_statement(self) -> str:
        title = self._proposal["title"]
        body = self._proposal["body"]
        return f"{title}\n\n{body}"

    @property
    def personal_statement(self) -> str:
        statement = ""
        if self._profile.first_name:
            statement += f"The user's name is {self._profile.first_name} "
        if self._profile.last_name:
            statement += f"{self._profile.last_name}. "
        if self._profile.bio:
            statement += f"Here is their bio: {self._profile.bio}"
        return statement


class CompletionResponse:
    """
    A class to encapsulating the response received from a Language Model
    (LLM) provider.

    Attributes
    ----------
    model : str
        The model used for the completion.
    created : int
        The timestamp when the completion was created.
    completion : str
        The completion result.
    usage : Usage
        The usage details of the completion.

    Classes
    -------
    Usage
        Represents the token usage in the completion response.

    """

    class Usage:
        """
        Represents the token usage in the completion response.

        Attributes
        ----------
        prompt_tokens : int
            The number of tokens used in the prompt.
        completion_tokens : int
            The number of tokens used in the completion.
        total_tokens : int
            The total number of tokens used.
        """

        prompt_tokens: int
        completion_tokens: int
        total_tokens: int

        def __init__(self, prompt_tokens, completion_tokens, total_tokens):
            self.prompt_tokens = prompt_tokens
            self.completion_tokens = completion_tokens
            self.total_tokens = total_tokens

    model: str
    created: int
    completion: str
    usage: Usage

    def __init__(self, model, created, completion, usage):
        self.model = model
        self.created = created
        self.completion = completion
        self.usage = usage


def openai_provider_completion(completion_request: CompletionRequest):
    """
    Generates a completion using the OpenAI provider.

    Parameters
    ----------
    completion_request : CompletionRequest
        The request object containing details for generating a completion.

    Returns
    -------
    CompletionResponse
        The response object containing the completion result.
    """
    with open(
        Path(__file__).parent
        / "text_templates"
        / "prompts"
        / "openai_provider_prompt.txt",
        "r",
    ) as prompt_file:
        prompt = prompt_file.read().format(
            about_statement=completion_request.about_statement,
            proposal_statement=completion_request.proposal_statement,
        )
        messages = [
            {
                "role": "system",
                "content": prompt,
            },
            {
                "role": "user",
                "content": completion_request.personal_statement,
            },
        ]

    completion = openai.ChatCompletion.create(
        model=completion_request.large_language_model,
        messages=messages,
    )

    return CompletionResponse(
        model=completion["model"],
        created=completion["created"],
        completion=completion["choices"][0]["message"]["content"],
        usage=CompletionResponse.Usage(
            prompt_tokens=completion["usage"]["prompt_tokens"],
            completion_tokens=completion["usage"]["completion_tokens"],
            total_tokens=completion["usage"]["total_tokens"],
        ),
    )


def meta_provider_completion(completion_request: CompletionRequest):
    """
    Generates a completion using the meta provider. (Not implemented)

    Parameters
    ----------
    completion_request : CompletionRequest
        The request object containing details for generating a completion.

    Raises
    ------
    NotImplementedError
        Always raised as this function is not yet implemented.
    """

    raise NotImplementedError("This function is not yet implemented.")
