import re
from typing import Any, List

from django import forms
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.template.defaultfilters import pluralize
from django.utils.text import get_text_list

from extra_views import InlineFormSetFactory
from model_utils import Choices
from model_utils.managers import InheritanceManager

from flare_portal.utils.validators import validate_ascending_order

from .. import constants
from .core import Nameable


class Manageable(Nameable):
    """URL methods for modules that are managed through the admin"""

    @classmethod
    def get_module_camel_case(cls) -> str:
        return re.sub("Module$", "", cls.__name__)

    @classmethod
    def get_create_path_name(cls) -> str:
        module_snake_case = cls.get_module_snake_case()
        return f"{module_snake_case}_create"

    @classmethod
    def get_create_path(cls) -> str:
        module_slug = cls.get_module_slug()
        return (
            "projects/<int:project_pk>/experiments/<int:experiment_pk>/modules/"
            f"{module_slug}/add/"
        )

    @classmethod
    def get_update_path_name(cls) -> str:
        module_snake_case = cls.get_module_snake_case()
        return f"{module_snake_case}_update"

    @classmethod
    def get_update_path(cls) -> str:
        module_slug = cls.get_module_slug()
        return (
            "projects/<int:project_pk>/experiments/<int:experiment_pk>/modules/"
            f"{module_slug}/<int:module_pk>/"
        )

    @classmethod
    def get_delete_path_name(cls) -> str:
        module_snake_case = cls.get_module_snake_case()
        return f"{module_snake_case}_delete"

    @classmethod
    def get_delete_path(cls) -> str:
        module_slug = cls.get_module_slug()
        return (
            "projects/<int:project_pk>/experiments/<int:experiment_pk>/modules/"
            f"{module_slug}/<int:module_pk>/delete/"
        )


class BaseModule(models.Model):
    exclude_fields: List[str] = []
    experiment = models.ForeignKey(
        "experiments.Experiment", on_delete=models.CASCADE, related_name="modules"
    )
    sortorder = models.PositiveIntegerField(default=0)

    objects = InheritanceManager()

    inlines: List[InlineFormSetFactory] = []

    class Meta:
        ordering = ["sortorder", "id"]

    def __str__(self) -> str:
        return f"PK: {self.pk} - Sort order: {self.sortorder}"

    @property
    def specific(self) -> Any:
        return BaseModule.objects.get_subclass(pk=self.pk)


class Module(Manageable, BaseModule):
    label = models.CharField(
        max_length=255,
        help_text=(
            "Helps with identifying modules. The label isn't displayed "
            "to the participant."
        ),
        blank=True,
    )

    class Meta:
        abstract = True

    def get_module_config(self) -> constants.ModuleConfigType:
        """Configuration returned by the config API for this module"""
        raise NotImplementedError()

    def get_module_default_title(self) -> str:
        """Short title for this module"""
        return self.get_module_name()

    def get_module_title(self) -> str:
        """Default or Reasearcher defined label"""
        return self.label or self.get_module_default_title()

    def get_module_subtitle(self) -> str:
        """Default or Reasearcher defined description"""
        if self.label:
            return f"{self.get_module_name()} - {self.get_module_description()}"

        return self.get_module_description()

    def get_module_description(self) -> str:
        """Short description of module configuration"""
        return ""


class FearConditioningModule(Module):
    PHASES = Choices(
        ("habituation", "Habituation"),
        ("acquisition", "Acquisition"),
        ("generalisation", "Generalisation"),
        ("extinction", "Extinction"),
        ("return_of_fear", "Return of fear"),
    )
    CONTEXTS = Choices(
        ("A", "Context A"),
        ("B", "Context B"),
        ("C", "Context C"),
    )
    phase = models.CharField(max_length=24, choices=PHASES, default=PHASES.habituation)
    trials_per_stimulus = models.PositiveIntegerField(default=0)
    reinforcement_rate = models.PositiveIntegerField(
        default=0, verbose_name="Number of reinforced CS+ trials"
    )
    generalisation_stimuli_enabled = models.BooleanField(default=False)
    context = models.CharField(max_length=1, choices=CONTEXTS, blank=True)

    def get_module_config(self) -> constants.ModuleConfigType:
        return constants.ModuleConfigType(
            id=self.pk,
            type=self.get_module_tag(),
            config={
                "phase": self.phase,
                "trials_per_stimulus": self.trials_per_stimulus,
                "reinforcement_rate": self.reinforcement_rate,
                "generalisation_stimuli_enabled": self.generalisation_stimuli_enabled,
                "context": self.context,
            },
        )

    def get_module_default_title(self) -> str:
        return self.get_phase_display()

    def get_module_description(self) -> str:
        details = [
            f"Trials per stimulus: {self.trials_per_stimulus}",
            f"Number of reinforced CS+ trials: {self.reinforcement_rate}",
            f"GS: {'Enabled' if self.generalisation_stimuli_enabled else 'Disabled'}",
            f"Context: {self.context if self.context else 'None'}",
        ]
        return ", ".join(details)

    def clean(self) -> None:
        if self.reinforcement_rate > self.trials_per_stimulus:
            raise ValidationError(
                {
                    "reinforcement_rate": "Number of reinforced CS+ trials "
                    "cannot be greater than the number of trials per stimulus."
                }
            )

        # Check context selection. The selected context must be populated on
        # the experiment to be configured.
        if (
            (self.context == "A" and not self.experiment.context_a)
            or (self.context == "B" and not self.experiment.context_b)
            or (self.context == "C" and not self.experiment.context_c)
        ):
            raise ValidationError(
                {"context": "The selected context is not set on the experiment."}
            )

    def __str__(self) -> str:
        return "Fear conditioning - " + super().__str__()


class BasicInfoModule(Module):
    collect_date_of_birth = models.BooleanField(default=False)
    collect_gender = models.BooleanField(default=False)
    collect_headphone_make = models.BooleanField(default=False)
    collect_headphone_model = models.BooleanField(default=False)
    collect_headphone_label = models.BooleanField(default=False)

    exclude_fields = [
        "collect_headphone_label",
        "collect_headphone_model",
        "collect_headphone_make",
    ]

    def get_module_config(self) -> constants.ModuleConfigType:
        return constants.ModuleConfigType(
            id=self.pk,
            type=self.get_module_tag(),
            config={
                "collect_date_of_birth": self.collect_date_of_birth,
                "collect_gender": self.collect_gender,
                "collect_headphone_make": self.collect_headphone_make,
                "collect_headphone_model": self.collect_headphone_model,
                "collect_headphone_label": self.collect_headphone_label,
            },
        )

    def get_module_description(self) -> str:
        collecting = {
            "date of birth": self.collect_date_of_birth,
            "gender": self.collect_gender,
            "headphone type": True,
            # "headphone make": self.collect_headphone_make,
            # "headphone model": self.collect_headphone_model,
            # "headphone label": self.collect_headphone_label,
            "device make and model": True,
            "OS name and version": True,
        }
        text = get_text_list([key for key, value in collecting.items() if value], "and")
        return "Collecting " + text

    def __str__(self) -> str:
        return "Basic info - " + super().__str__()


class CriterionQuestion(models.Model):
    question_text = models.CharField(max_length=255)
    help_text = models.TextField(blank=True)
    correct_answer = models.BooleanField(
        default=None,
        null=True,
        blank=True,
        choices=(
            (None, "Yes or No"),
            (True, "Yes"),
            (False, "No"),
        ),
    )
    required = models.BooleanField(default=True)

    module = models.ForeignKey(
        "experiments.CriterionModule",
        on_delete=models.CASCADE,
        related_name="questions",
    )
    sortorder = models.PositiveIntegerField(default=0)

    inline_label = "Questions"

    def __str__(self) -> str:
        return self.question_text


class CriterionQuestionInline(InlineFormSetFactory):
    model = CriterionQuestion
    fields = ["question_text", "help_text", "correct_answer", "required", "sortorder"]
    factory_kwargs = {"widgets": {"sortorder": forms.HiddenInput}, "extra": 0}


class CriterionModule(Module):
    intro_text = models.TextField(blank=True)

    inlines = [CriterionQuestionInline]

    def get_module_config(self) -> constants.ModuleConfigType:
        return constants.ModuleConfigType(
            id=self.pk,
            type=self.get_module_tag(),
            config={
                "intro_text": self.intro_text,
                "questions": [
                    {
                        "id": question.pk,
                        "help_text": question.help_text,
                        "question_text": question.question_text,
                        "correct_answer": question.correct_answer,
                        "required": question.required,
                    }
                    for question in self.questions.all()
                ],
            },
        )

    def get_module_description(self) -> str:
        question_count = self.questions.count()
        return f"{question_count} question{pluralize(question_count)}"

    def __str__(self) -> str:
        return "Criterion - " + super().__str__()


class WebModule(Module):
    heading = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    url = models.URLField(verbose_name="URL")
    auto_close_url = models.URLField(
        blank=True,
        verbose_name="Automatic close URL",
        help_text="Optional: Enter a URL here that if redirected to will "
        "automatically close this module.",
    )
    append_participant_id = models.BooleanField(
        blank=True,
        help_text="Optional: Enabling this feature will append the "
        "participant's id to the url. This is useful if you are using a "
        "survey service such as Qualtrics or Google Forms.",
    )

    def get_module_config(self) -> constants.ModuleConfigType:
        return constants.ModuleConfigType(
            id=self.pk,
            type=self.get_module_tag(),
            config={
                "heading": self.heading,
                "description": self.description,
                "url": self.url,
                "append_participant_id": self.append_participant_id,
                "auto_close_url": self.auto_close_url,
            },
        )

    def get_module_description(self) -> str:
        return f"{self.heading} ({self.url})"

    def __str__(self) -> str:
        return "Web - " + super().__str__()


class InstructionsScreen(models.Model):
    title = models.CharField(max_length=255)
    body = models.TextField(blank=True)
    action_label = models.CharField(
        max_length=255,
        blank=True,
        help_text='This text appears just above the "Next" button.',
    )

    module = models.ForeignKey(
        "experiments.InstructionsModule",
        on_delete=models.CASCADE,
        related_name="screens",
    )

    inline_label = "Screens"

    def __str__(self) -> str:
        return self.title


class InstructionsScreenInline(InlineFormSetFactory):
    model = InstructionsScreen
    fields = ["title", "body", "action_label"]
    factory_kwargs = {"extra": 0}


def get_volume_increments() -> List[float]:
    return [0.5, 0.65, 0.8, 0.9, 0.95, 1]


class InstructionsModule(Module):
    include_volume_calibration = models.BooleanField(
        default=False,
        help_text=(
            "Enabling volume calibration will override the US file "
            "volume set in the experiment settings."
        ),
    )
    volume_increments = ArrayField(
        models.FloatField(
            blank=False,
            validators=[MinValueValidator(0), MaxValueValidator(1)],
        ),
        size=6,
        default=get_volume_increments,
        validators=[validate_ascending_order],
    )
    end_screen_title = models.CharField(max_length=255, blank=True)
    end_screen_body = models.TextField(
        blank=True,
        help_text=(
            "The end screen will not be displayed if both the title and body "
            "are left blank."
        ),
    )

    inlines = [InstructionsScreenInline]

    def get_module_config(self) -> constants.ModuleConfigType:
        return constants.ModuleConfigType(
            id=self.pk,
            type=self.get_module_tag(),
            config={
                "include_volume_calibration": self.include_volume_calibration,
                "volume_increments": self.volume_increments,
                "end_screen_title": self.end_screen_title,
                "end_screen_body": self.end_screen_body,
                "screens": [
                    {
                        "title": screen.title,
                        "body": screen.body,
                        "action_label": screen.action_label,
                    }
                    for screen in self.screens.all()
                ],
            },
        )

    @classmethod
    def get_module_name(cls) -> str:
        return "Setup Instructions"

    def get_module_description(self) -> str:
        screen_count = self.screens.count()
        return f"{screen_count} screen{pluralize(screen_count)}"

    def __str__(self) -> str:
        return "Instructions - " + super().__str__()


class AffectiveRatingModule(Module):
    question = models.CharField(
        max_length=255, default="Have you seen this image before?"
    )
    generalisation_stimuli_enabled = models.BooleanField(default=False)

    rating_scale_anchor_label_left = models.CharField(
        max_length=255, default="Definitely never seen before"
    )
    rating_scale_anchor_label_center = models.CharField(
        max_length=255, default="Neutral"
    )
    rating_scale_anchor_label_right = models.CharField(
        max_length=255, default="Definitely have seen before"
    )

    def get_module_config(self) -> constants.ModuleConfigType:
        return constants.ModuleConfigType(
            id=self.pk,
            type=self.get_module_tag(),
            config={
                # fmt: off
                "question": self.question,
                "generalisation_stimuli_enabled": self.generalisation_stimuli_enabled,
                "rating_scale_anchor_label_left": self.rating_scale_anchor_label_left,
                "rating_scale_anchor_label_center":
                    self.rating_scale_anchor_label_center,
                "rating_scale_anchor_label_right": self.rating_scale_anchor_label_right,
                # fmt: on
            },
        )

    def get_module_default_title(self) -> str:
        return self.__str__()

    def get_module_description(self) -> str:
        return self.question

    def __str__(self) -> str:
        if self.generalisation_stimuli_enabled:
            return "Affective Rating (CS/GS)"

        return "Affective Rating (CS)"


class TextModule(Module):
    heading = models.CharField(max_length=255)
    body = models.TextField(blank=True)

    def get_module_config(self) -> constants.ModuleConfigType:
        return constants.ModuleConfigType(
            id=self.pk,
            type=self.get_module_tag(),
            config={"heading": self.heading, "body": self.body},
        )

    def get_module_default_title(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"Text - {self.heading}"


class BreakStartModule(Module):
    duration = models.PositiveIntegerField(
        help_text="How long the break should last in seconds (e.g. 300 is 5 minutes).",
    )
    start_title = models.CharField(
        max_length=255,
        help_text="Displays on the start break screen.",
    )
    start_body = models.TextField(
        blank=True,
        help_text="Displays on the start break screen.",
    )
    end_title = models.CharField(
        max_length=255,
        help_text="Displays on the end break screen.",
    )
    end_body = models.TextField(
        blank=True,
        help_text="Displays on the end break screen.",
    )

    @classmethod
    def get_module_name(cls) -> str:
        return "Break"

    @classmethod
    def get_module_tag(cls) -> str:
        return "BREAK_START"

    def get_module_title(self) -> str:
        if self.label:
            return f"Break start - {self.label}"

        return "Break start"

    def get_module_config(self) -> constants.ModuleConfigType:
        return constants.ModuleConfigType(
            id=self.pk,
            type=self.get_module_tag(),
            config={
                "duration": self.duration,
                "start_title": self.start_title,
                "start_body": self.start_body,
            },
        )

    def get_module_description(self) -> str:
        return f"Duration: {self.duration} second{pluralize(self.duration)}"

    def __str__(self) -> str:
        return "Break start - " + super().__str__()


class BreakEndModule(BaseModule):
    # Define one-to-one relationship from here so that when the start module is
    # deleted, the end module is also deleted
    start_module = models.OneToOneField(
        "experiments.BreakStartModule",
        on_delete=models.CASCADE,
        related_name="end_module",
    )

    def get_module_title(self) -> str:
        if self.start_module.label:
            return f"Break end - {self.start_module.label}"

        return "Break end"

    def get_module_config(self) -> constants.ModuleConfigType:
        return constants.ModuleConfigType(
            id=self.pk,
            type="BREAK_END",
            config={
                "end_title": self.start_module.end_title,
                "end_body": self.start_module.end_body,
            },
        )

    def __str__(self) -> str:
        return "Break end - " + super().__str__()


class TaskInstructionsModule(Module):
    intro_heading = models.CharField(
        max_length=255,
        default="Practice time",
        help_text="Title on the task instructions intro screen",
    )
    intro_body = models.TextField(
        blank=True,
        default="Before you begin the experiment, we need to "
        "practice using the rating interface.",
        help_text="Text on the task instructions intro screen",
    )
    rating_explanation_heading = models.CharField(
        max_length=255,
        default="A few seconds after each circle appears, this scale will appear "
        "at the bottom of the screen.",
        help_text="Title on the rating scale explanation screen",
    )
    rating_explanation_body = models.TextField(
        blank=True,
        default="Each time the scale appears, press the corresponding number on "
        "the screen to rate how much you expect to hear a scream.",
        help_text="Text on the rating scale explanation screen",
    )
    rating_practice_heading = models.TextField(
        default="Press any number to practice making a rating with the scale below.",
        help_text="Text on the rating scale practice screen",
    )
    interval_explanation_body = models.TextField(
        default="Before each circle is presented, you will see a white screen "
        "with a cross in the middle like the one shown above. It is important "
        "that you keep looking at the cross and wait for the next circle to appear.",
        help_text="Text on the ITI explanation screen",
    )
    outro_heading = models.CharField(
        max_length=255,
        default="Instructions complete",
        help_text="Title on the task instructions outro screen",
    )
    outro_body = models.TextField(
        blank=True,
        default="The experiment will now begin.\n\nYou may occasionally hear a "
        "scream.\n\nRemember to rate how much you expect to hear a scream by "
        "pressing a number every time the scale appears.",
        help_text="Text on the task instructions outro screen",
    )

    def get_module_config(self) -> constants.ModuleConfigType:
        return constants.ModuleConfigType(
            id=self.pk,
            type=self.get_module_tag(),
            config={
                "intro_heading": self.intro_heading,
                "intro_body": self.intro_body,
                "rating_explanation_heading": self.rating_explanation_heading,
                "rating_explanation_body": self.rating_explanation_body,
                "rating_practice_heading": self.rating_practice_heading,
                "interval_explanation_body": self.interval_explanation_body,
                "outro_heading": self.outro_heading,
                "outro_body": self.outro_body,
            },
        )

    def __str__(self) -> str:
        return "Task instructions - " + super().__str__()


class PostExperimentQuestionsModule(Module):
    heading = models.CharField(
        max_length=255,
        default="Review Questions",
        help_text="Title at the top of the questions screen",
    )

    experiment_unpleasant_rating = models.BooleanField(
        verbose_name="How unpleasant did you find the experiment with the loud "
        "noises?",
    )

    did_follow_instructions = models.BooleanField(
        verbose_name="Did you follow the instructions fully during the session?",
    )

    did_remove_headphones = models.BooleanField(
        verbose_name="Did you remove your headphones at any point during the "
        "experiment?",
    )

    did_pay_attention = models.BooleanField(
        verbose_name="Were you paying attention throughout the task where you "
        "were rating images?",
    )

    task_environment = models.BooleanField(
        verbose_name="Where did you do the task?",
    )

    was_quiet = models.BooleanField(
        verbose_name="Was the place where you did the task quiet?",
    )

    was_not_alone = models.BooleanField(
        verbose_name="Were there any other people in the room (or passing by) "
        "while you were doing the task?",
    )

    was_interrupted = models.BooleanField(
        verbose_name="Were you interrupted during the task?",
    )

    def get_module_config(self) -> constants.ModuleConfigType:
        return constants.ModuleConfigType(
            id=self.pk,
            type=self.get_module_tag(),
            config={
                "heading": self.heading,
                "questions": {
                    "experiment_unpleasant_rating": self.experiment_unpleasant_rating,
                    "did_follow_instructions": self.did_follow_instructions,
                    "did_remove_headphones": self.did_remove_headphones,
                    "did_pay_attention": self.did_pay_attention,
                    "task_environment": self.task_environment,
                    "was_quiet": self.was_quiet,
                    "was_not_alone": self.was_not_alone,
                    "was_interrupted": self.was_interrupted,
                },
            },
        )


class USUnpleasantnessModule(Module):
    audible_keyword = models.CharField(
        max_length=255, help_text="How unpleasant did you find the ......?"
    )

    def get_module_config(self) -> constants.ModuleConfigType:
        return constants.ModuleConfigType(
            id=self.pk,
            type=self.get_module_tag(),
            config={"question": self.construct_question()},
        )

    def construct_question(self) -> str:
        return f"How unpleasant did you find the {self.audible_keyword}?"

    @classmethod
    def get_module_name(cls) -> str:
        return "US Unpleasantness"

    def get_module_description(self) -> str:
        return self.construct_question()


def construct_awareness_question(first_keyword: str, second_keyword: str) -> str:
    return (
        "Did you happen to notice whether you heard the "
        + f"{first_keyword} after seeing a certain {second_keyword}?"
    )


class ContingencyAwarenessModule(Module):
    audible_keyword = models.CharField(
        max_length=255,
        help_text=construct_awareness_question("......", "stimuli"),
    )
    visual_keyword = models.CharField(
        max_length=255,
        help_text=construct_awareness_question("sound", "......"),
    )

    def get_module_config(self) -> constants.ModuleConfigType:
        return constants.ModuleConfigType(
            id=self.pk,
            type=self.get_module_tag(),
            config={
                "awareness_question": construct_awareness_question(
                    self.audible_keyword, self.visual_keyword
                ),
                "confirmation_question": f"Which {self.visual_keyword} "
                f"did you associate with the {self.audible_keyword}?",
            },
        )

    def get_module_description(self) -> str:
        return construct_awareness_question(self.audible_keyword, self.visual_keyword)
