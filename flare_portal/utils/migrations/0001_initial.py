# -*- coding: utf-8 -*-
# Generated by Django 1.10.7 on 2017-04-14 09:23
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import wagtail.core.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("images", "0001_initial"),
        ("wagtailcore", "0032_add_bulk_delete_page_permission"),
    ]

    operations = [
        migrations.CreateModel(
            name="CallToActionSnippet",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255)),
                (
                    "link",
                    wagtail.core.fields.StreamField(
                        (
                            (
                                "external_link",
                                wagtail.core.blocks.StructBlock(
                                    (
                                        ("url", wagtail.core.blocks.URLBlock()),
                                        ("title", wagtail.core.blocks.CharBlock()),
                                    ),
                                    icon="link",
                                ),
                            ),
                            (
                                "internal_link",
                                wagtail.core.blocks.StructBlock(
                                    (
                                        (
                                            "page",
                                            wagtail.core.blocks.PageChooserBlock(),
                                        ),
                                        (
                                            "title",
                                            wagtail.core.blocks.CharBlock(
                                                required=False
                                            ),
                                        ),
                                    ),
                                    icon="link",
                                ),
                            ),
                        ),
                        blank=True,
                    ),
                ),
                (
                    "summary",
                    wagtail.core.fields.RichTextField(blank=True, max_length=255),
                ),
                (
                    "image",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="+",
                        to="images.CustomImage",
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="SocialMediaSettings",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "twitter_handle",
                    models.CharField(
                        blank=True,
                        help_text="Your Twitter username without the @, e.g. katyperry",
                        max_length=255,
                    ),
                ),
                (
                    "facebook_app_id",
                    models.CharField(
                        blank=True, help_text="Your Facebook app ID.", max_length=255
                    ),
                ),
                (
                    "default_sharing_text",
                    models.CharField(
                        blank=True,
                        help_text="Default sharing text to use if social text has not been set on a page.",
                        max_length=255,
                    ),
                ),
                (
                    "site_name",
                    models.CharField(
                        blank=True,
                        default="Flare Portal",
                        help_text="Site name, used by Open Graph.",
                        max_length=255,
                    ),
                ),
                (
                    "site",
                    models.OneToOneField(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="wagtailcore.Site",
                    ),
                ),
            ],
            options={"abstract": False},
        ),
        migrations.CreateModel(
            name="SystemMessagesSettings",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "title_404",
                    models.CharField(
                        default="Page not found", max_length=255, verbose_name="Title"
                    ),
                ),
                (
                    "body_404",
                    wagtail.core.fields.RichTextField(
                        default="<p>You may be trying to find a page that doesn&rsquo;t exist or has been moved.</p>",
                        verbose_name="Text",
                    ),
                ),
                (
                    "site",
                    models.OneToOneField(
                        editable=False,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="wagtailcore.Site",
                    ),
                ),
            ],
            options={"abstract": False, "verbose_name": "system messages"},
        ),
    ]
