from decimal import Decimal

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from rest_framework.serializers import DateTimeField

from flare_portal.experiments.factories import (
    AffectiveRatingModuleFactory,
    CriterionModuleFactory,
    CriterionQuestionFactory,
    ExperimentFactory,
    FearConditioningModuleFactory,
    ParticipantFactory,
)
from flare_portal.experiments.models import (
    Experiment,
    FearConditioningModule,
    Participant,
)
from flare_portal.reimbursement.factories import VoucherFactory, VoucherPoolFactory
from flare_portal.site_config.models import SiteConfiguration

test_file = "flare_portal/experiments/tests/assets/circle.png"


def get_example_experiment() -> Experiment:
    us_file = SimpleUploadedFile("file.wav", b"wav content", content_type="audio/wav")
    csa_file = SimpleUploadedFile(
        "csa.png", open(test_file, "rb").read(), content_type="image/png"
    )
    csb_file = SimpleUploadedFile(
        "csa.png", open(test_file, "rb").read(), content_type="image/png"
    )
    context_a_file = SimpleUploadedFile(
        "context_a.png",
        open(test_file, "rb").read(),
        content_type="image/png",
    )
    context_b_file = SimpleUploadedFile(
        "context_b.png",
        open(test_file, "rb").read(),
        content_type="image/png",
    )
    return ExperimentFactory(
        us=us_file,
        csa=csa_file,
        csb=csb_file,
        context_a=context_a_file,
        context_b=context_b_file,
    )


class ConfigurationAPIViewTest(TestCase):
    def test_post(self) -> None:
        config = SiteConfiguration.get_solo()
        config.terms_and_conditions = "Some T&Cs"
        config.save()

        experiment: Experiment = get_example_experiment()
        ParticipantFactory(participant_id="Flare.ABCDEF", experiment=experiment)

        module1: FearConditioningModule = FearConditioningModuleFactory(
            experiment=experiment, sortorder=1
        )

        module2: FearConditioningModule = FearConditioningModuleFactory(
            experiment=experiment, sortorder=2
        )

        resp = self.client.post(
            reverse("api:configuration"),
            {"participant": "Flare.ABCDEF"},
            content_type="application/json",
        )

        self.assertEqual(200, resp.status_code)

        data = resp.json()

        self.assertEqual(
            data["experiment"],
            {
                "id": experiment.pk,
                "name": experiment.name,
                "description": experiment.description,
                "contact_email": None,
                "trial_length": experiment.trial_length,
                "rating_delay": experiment.rating_delay,
                "iti_min_delay": experiment.iti_min_delay,
                "iti_max_delay": experiment.iti_max_delay,
                "rating_scale_anchor_label_left": (
                    experiment.rating_scale_anchor_label_left
                ),
                "rating_scale_anchor_label_center": (
                    experiment.rating_scale_anchor_label_center
                ),
                "rating_scale_anchor_label_right": (
                    experiment.rating_scale_anchor_label_right
                ),
                "us": experiment.us.url,
                "csa": experiment.csa.url,
                "csb": experiment.csb.url,
                "context_a": experiment.context_a.url,
                "context_b": experiment.context_b.url,
                "context_c": None,
                "gsa": None,
                "gsb": None,
                "gsc": None,
                "gsd": None,
                "reimbursements": False,
            },
        )
        self.assertEqual(
            data["config"],
            {
                "terms_and_conditions": "Some T&Cs",
            },
        )
        self.assertEqual(
            data["modules"],
            [
                {
                    "id": module1.pk,
                    "type": "FEAR_CONDITIONING",
                    "config": {
                        "phase": module1.phase,
                        "trials_per_stimulus": module1.trials_per_stimulus,
                        "reinforcement_rate": module1.reinforcement_rate,
                        "generalisation_stimuli_enabled": (
                            module1.generalisation_stimuli_enabled
                        ),
                        "context": module1.context,
                    },
                },
                {
                    "id": module2.pk,
                    "type": "FEAR_CONDITIONING",
                    "config": {
                        "phase": module2.phase,
                        "trials_per_stimulus": module2.trials_per_stimulus,
                        "reinforcement_rate": module2.reinforcement_rate,
                        "generalisation_stimuli_enabled": (
                            module2.generalisation_stimuli_enabled
                        ),
                        "context": module2.context,
                    },
                },
            ],
        )

    def test_validation(self) -> None:
        resp = self.client.post(
            reverse("api:configuration"), {"participant": "Flare.ABCDEF"}
        )

        self.assertEqual(400, resp.status_code)

        self.assertEqual(
            resp.json(),
            {
                "participant": [
                    "This participant identifier is not correct, please contact "
                    "your research assistant."
                ]
            },
        )


class SubmissionAPIViewTest(TestCase):
    def test_post(self) -> None:
        experiment: Experiment = get_example_experiment()
        participant = ParticipantFactory(
            participant_id="Flare.ABCDEF", experiment=experiment
        )

        # Try to finish the experiment
        submit_resp = self.client.post(
            reverse("api:submission"),
            {"participant": "Flare.ABCDEF"},
            content_type="application/json",
        )

        # Test that the request fails because it hasn't started
        self.assertEqual(400, submit_resp.status_code)

        # Test that the configuration object can only be retrived once
        config_resp = self.client.post(
            reverse("api:configuration"),
            {"participant": "Flare.ABCDEF"},
            content_type="application/json",
        )
        self.assertEqual(200, config_resp.status_code)
        config_resp = self.client.post(
            reverse("api:configuration"),
            {"participant": "Flare.ABCDEF"},
            content_type="application/json",
        )
        self.assertEqual(400, config_resp.status_code)

        # Finish experiment & Test response
        submit_resp = self.client.post(
            reverse("api:submission"),
            {"participant": "Flare.ABCDEF"},
            content_type="application/json",
        )
        submit_data = submit_resp.json()
        updated_participant = Participant.objects.get(pk=participant.id)
        self.assertEqual(200, submit_resp.status_code)
        self.assertEqual(
            submit_data["participant_started_at"],
            DateTimeField().to_representation(updated_participant.started_at),
        )
        self.assertEqual(
            submit_data["participant_finished_at"],
            DateTimeField().to_representation(updated_participant.finished_at),
        )


class TermsAndConditionsAPIViewTest(TestCase):
    def test_agree_to_terms(self) -> None:
        participant = ParticipantFactory(participant_id="Flare.ABCDEF")

        resp = self.client.post(
            reverse("api:terms_and_conditions"),
            {"participant": "Flare.ABCDEF"},
            content_type="application/json",
        )

        self.assertEqual(200, resp.status_code)

        self.assertEqual(
            resp.json(),
            {
                "participant": "Flare.ABCDEF",
                "agreed_to_terms_and_conditions": True,
            },
        )

        participant.refresh_from_db()

        self.assertTrue(participant.agreed_to_terms_and_conditions)


class ModuleDataAPIViewTest(TestCase):
    def test_post(self) -> None:
        experiment: Experiment = ExperimentFactory()
        module: FearConditioningModule = FearConditioningModuleFactory(
            experiment=experiment
        )
        participant: Participant = ParticipantFactory(experiment=experiment)

        url = reverse("api:fear_conditioning_data")

        json_data = {
            "participant": participant.participant_id,
            "module": module.pk,
            "trial": 1,
            "rating": 5,
            "conditional_stimulus": "CSA",
            "unconditional_stimulus": True,
            "trial_started_at": parse_datetime("2020-01-01T00:00Z"),
            "response_recorded_at": parse_datetime("2020-01-01T00:00Z"),
            "volume_level": "0.50",
            "calibrated_volume_level": "0.85",
            "headphones": True,
        }

        resp = self.client.post(url, json_data, content_type="application/json")

        self.assertEqual(201, resp.status_code)

        # Verify data posted
        data = module.data.get()

        response_data = {
            **resp.json(),
            "trial_started_at": parse_datetime(resp.json()["trial_started_at"]),
            "response_recorded_at": parse_datetime(resp.json()["response_recorded_at"]),
        }

        self.assertEqual(response_data, {**json_data, "id": data.pk})

        self.assertEqual(data.participant.participant_id, json_data["participant"])
        self.assertEqual(data.module_id, json_data["module"])
        self.assertEqual(data.trial, json_data["trial"])
        self.assertEqual(data.rating, json_data["rating"])
        self.assertEqual(data.conditional_stimulus, json_data["conditional_stimulus"])
        self.assertEqual(
            data.unconditional_stimulus, json_data["unconditional_stimulus"]
        )
        self.assertEqual(data.trial_started_at, json_data["trial_started_at"])
        self.assertEqual(data.response_recorded_at, json_data["response_recorded_at"])
        self.assertEqual(data.volume_level, Decimal(json_data["volume_level"]))
        self.assertEqual(
            data.calibrated_volume_level, Decimal(json_data["calibrated_volume_level"])
        )
        self.assertEqual(data.headphones, json_data["headphones"])

    def test_validation(self) -> None:
        # Should not be able to add data for a participant that is not in the
        # same experiment as the module
        module: FearConditioningModule = FearConditioningModuleFactory()
        participant: Participant = ParticipantFactory()

        url = reverse("api:fear_conditioning_data")

        json_data = {
            "participant": participant.participant_id,
            "module": module.pk,
            "trial": 1,
            "rating": 5,
            "conditional_stimulus": "CSA",
            "unconditional_stimulus": True,
            "trial_started_at": parse_datetime("2020-01-01T00:00Z"),
            "response_recorded_at": parse_datetime("2020-01-01T00:00Z"),
            "volume_level": 0.50,
            "calibrated_volume_level": 0.85,
            "headphones": True,
        }

        resp = self.client.post(url, json_data, content_type="application/json")

        self.assertEqual(400, resp.status_code)

        self.assertEqual(
            resp.json(),
            {
                "participant": [
                    "This participant is not part of the module's experiment."
                ]
            },
        )


class FearConditioningDataAPIViewTest(TestCase):
    def test_unique_trial(self) -> None:
        experiment: Experiment = ExperimentFactory()
        module: FearConditioningModule = FearConditioningModuleFactory(
            experiment=experiment
        )
        participant: Participant = ParticipantFactory(experiment=experiment)

        url = reverse("api:fear_conditioning_data")

        json_data = {
            "participant": participant.participant_id,
            "module": module.pk,
            "trial": 1,
            "rating": 5,
            "conditional_stimulus": "CSA",
            "unconditional_stimulus": True,
            "trial_started_at": parse_datetime("2020-01-01T00:00Z"),
            "response_recorded_at": parse_datetime("2020-01-01T00:00Z"),
            "volume_level": "0.50",
            "calibrated_volume_level": "0.85",
            "headphones": True,
        }

        resp = self.client.post(url, json_data, content_type="application/json")

        self.assertEqual(201, resp.status_code)

        # Send the same data again (same trial, participant, and module)
        resp = self.client.post(url, json_data, content_type="application/json")

        self.assertEqual(400, resp.status_code)

        self.assertEqual(
            resp.json(),
            {
                "non_field_errors": [
                    "The fields trial, module, participant must make a unique set."
                ]
            },
        )


class CriterionDataAPIViewTest(TestCase):
    def test_post(self) -> None:
        experiment = ExperimentFactory()
        participant = ParticipantFactory(experiment=experiment)
        module = CriterionModuleFactory(experiment=experiment)

        question_1 = CriterionQuestionFactory(module=module)
        question_2 = CriterionQuestionFactory(module=module)

        url = reverse("api:criterion_data")

        json_data = {
            "participant": participant.participant_id,
            "module": module.pk,
            "question": question_1.pk,
            "answer": True,
        }

        resp = self.client.post(url, json_data, content_type="application/json")

        self.assertEqual(201, resp.status_code)

        json_data = {
            "participant": participant.participant_id,
            "module": module.pk,
            "question": question_2.pk,
            "answer": False,
        }

        resp = self.client.post(url, json_data, content_type="application/json")

        self.assertEqual(201, resp.status_code)

        answers = module.data.all()

        self.assertEqual(answers[0].question, question_1)
        self.assertEqual(answers[0].answer, True)

        self.assertEqual(answers[1].question, question_2)
        self.assertEqual(answers[1].answer, False)

    def test_unique_answer(self) -> None:
        experiment = ExperimentFactory()
        participant = ParticipantFactory(experiment=experiment)
        module = CriterionModuleFactory(experiment=experiment)

        question_1 = CriterionQuestionFactory(module=module)

        url = reverse("api:criterion_data")

        # Participant can only submit one answer to a question
        json_data = {
            "participant": participant.participant_id,
            "module": module.pk,
            "question": question_1.pk,
            "answer": True,
        }

        resp = self.client.post(url, json_data, content_type="application/json")

        self.assertEqual(201, resp.status_code)

        json_data = {
            "participant": participant.participant_id,
            "module": module.pk,
            "question": question_1.pk,
            "answer": True,
        }

        resp = self.client.post(url, json_data, content_type="application/json")

        # Error
        self.assertEqual(400, resp.status_code)
        self.assertEqual(
            resp.json(),
            {
                "non_field_errors": [
                    "The fields participant, question must make a unique set."
                ]
            },
        )

    def test_question_validation(self) -> None:
        # Question should belong to the module
        experiment = ExperimentFactory()
        participant = ParticipantFactory(experiment=experiment)
        module = CriterionModuleFactory(experiment=experiment)

        question_1 = CriterionQuestionFactory()

        url = reverse("api:criterion_data")

        # Participant can only submit one answer to a question
        json_data = {
            "participant": participant.participant_id,
            "module": module.pk,
            "question": question_1.pk,
            "answer": True,
        }

        resp = self.client.post(url, json_data, content_type="application/json")

        self.assertEqual(400, resp.status_code)

        self.assertEqual(
            resp.json(), {"question": ["This question does not belong to that module."]}
        )


class AffectiveRatingAPIViewTest(TestCase):
    def test_post(self) -> None:
        experiment = ExperimentFactory()
        participant = ParticipantFactory(experiment=experiment)
        module = AffectiveRatingModuleFactory(experiment=experiment)

        url = reverse("api:affective_rating_data")

        json_data = {
            "participant": participant.participant_id,
            "module": module.pk,
            "rating": 5,
            "stimulus": "csa",
        }

        resp = self.client.post(url, json_data, content_type="application/json")

        # Check valid submission
        self.assertEqual(201, resp.status_code)

        # Check submitted data is valid
        data = module.data.first()
        self.assertEqual(data.rating, json_data["rating"])
        self.assertEqual(data.stimulus, json_data["stimulus"])


class VoucherAPIViewTest(TestCase):
    def setUp(self) -> None:
        self.url = reverse("api:voucher")

    def test_get_voucher(self) -> None:
        voucher = VoucherFactory(pool__success_message="Use this on Amazon")
        experiment = ExperimentFactory(voucher_pool=voucher.pool)
        participant = ParticipantFactory(
            experiment=experiment,
            started_at=timezone.now(),
            finished_at=timezone.now(),
        )

        post_data = {
            "participant": participant.participant_id,
        }

        resp = self.client.post(self.url, post_data)

        self.assertEqual(200, resp.status_code)

        self.assertEqual(
            resp.json(),
            {
                "status": "success",
                "voucher": voucher.code,
                "success_message": voucher.pool.success_message,
            },
        )

        voucher.refresh_from_db()

        self.assertEqual(voucher.participant, participant)

    def test_voucher_pool_empty(self) -> None:
        voucher = VoucherFactory(pool__empty_pool_message="No codes left.")
        pool = voucher.pool
        experiment = ExperimentFactory(voucher_pool=pool)
        participant_1 = ParticipantFactory(
            experiment=experiment,
            started_at=timezone.now(),
            finished_at=timezone.now(),
        )
        participant_2 = ParticipantFactory(
            experiment=experiment,
            started_at=timezone.now(),
            finished_at=timezone.now(),
        )

        # Fetch voucher
        post_data = {
            "participant": participant_1.participant_id,
        }

        resp = self.client.post(self.url, post_data)

        self.assertEqual(200, resp.status_code)

        # Fetch voucher again, this time no more vouchers available
        post_data = {
            "participant": participant_2.participant_id,
        }

        resp = self.client.post(self.url, post_data)

        self.assertEqual(200, resp.status_code)

        self.assertEqual(
            resp.json(),
            {
                "status": "error",
                "error_code": "pool_empty",
                "error_message": pool.empty_pool_message,
            },
        )

    def test_voucher_pool_unassigned(self) -> None:
        experiment = ExperimentFactory()
        participant_1 = ParticipantFactory(
            experiment=experiment,
            started_at=timezone.now(),
            finished_at=timezone.now(),
        )

        post_data = {
            "participant": participant_1.participant_id,
        }

        resp = self.client.post(self.url, post_data)

        self.assertEqual(400, resp.status_code)

        self.assertEqual(
            resp.json(),
            {
                "status": "error",
                "error_code": "pool_unassigned",
                "error_message": "This experiment is not assigned a voucher pool",
            },
        )

    def test_participant_not_completed_experiment(self) -> None:
        voucher = VoucherFactory()
        experiment = ExperimentFactory(voucher_pool=voucher.pool)
        participant = ParticipantFactory(experiment=experiment)

        post_data = {
            "participant": participant.participant_id,
        }

        resp = self.client.post(self.url, post_data)

        self.assertEqual(400, resp.status_code)

    def test_participant_already_claimed_voucher(self) -> None:
        pool = VoucherPoolFactory()
        VoucherFactory.create_batch(5, pool=pool)
        experiment = ExperimentFactory(voucher_pool=pool)
        participant = ParticipantFactory(
            experiment=experiment,
            started_at=timezone.now(),
            finished_at=timezone.now(),
        )

        # Fetch voucher
        post_data = {
            "participant": participant.participant_id,
        }

        resp = self.client.post(self.url, post_data)

        self.assertEqual(200, resp.status_code)

        # Fetch voucher again, should return error
        resp = self.client.post(self.url, post_data)

        self.assertEqual(400, resp.status_code)


class TrackingAPIViewTest(TestCase):
    def test_post(self) -> None:
        experiment: Experiment = get_example_experiment()
        fc_module = FearConditioningModuleFactory(experiment=experiment)
        participant = ParticipantFactory(
            participant_id="Flare.ABCDEF", experiment=experiment
        )

        # Try to finish the experiment
        resp = self.client.post(
            reverse("api:tracking"),
            {
                "participant": participant.participant_id,
                "module": fc_module.pk,
                "trial_index": 1,
            },
            content_type="application/json",
        )

        # Test that current module has been updated
        self.assertEqual(
            resp.json(),
            {
                "participant": participant.participant_id,
                "current_module": fc_module.pk,
                "current_trial": 1,
                "rejection_reason": None,
            },
        )

        # Try to timeout the experiment
        resp = self.client.post(
            reverse("api:tracking"),
            {"participant": participant.participant_id, "rejection_reason": "TIMEOUT"},
            content_type="application/json",
        )

        # Test that current module has been reset
        self.assertEqual(
            resp.json(),
            {
                "participant": participant.participant_id,
                "rejection_reason": "TIMEOUT",
                "current_module": fc_module.pk,
                "current_trial": 1,
            },
        )
