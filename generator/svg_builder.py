"""SVG Builder — orchestrator connecting config, stats, and templates."""

from generator.templates import galaxy_header, stats_card, tech_stack, projects_constellation, about_card


class SVGBuilder:
    """Builds all SVG assets from config and GitHub data.

    Expects a config dict that has already been through validate_config(),
    which resolves theme defaults and applies missing optional fields.
    """

    def __init__(self, config: dict, stats: dict, languages: dict, activity: list = None):
        self.config = config
        self.stats = stats
        self.languages = languages
        self.activity = activity or []
        self.theme = config["theme"]
        self.galaxy_arms = config.get("galaxy_arms", [])
        self.projects = config.get("projects", [])

    def render_galaxy_header(self) -> str:
        return galaxy_header.render(
            config=self.config,
            theme=self.theme,
            galaxy_arms=self.galaxy_arms,
            projects=self.projects,
        )

    def render_stats_card(self) -> str:
        metrics = self.config["stats"]["metrics"]
        return stats_card.render(
            stats=self.stats,
            metrics=metrics,
            theme=self.theme,
            activity=self.activity,
        )

    def render_tech_stack(self) -> str:
        lang_config = self.config.get("languages", {})
        return tech_stack.render(
            languages=self.languages,
            galaxy_arms=self.galaxy_arms,
            theme=self.theme,
            exclude=lang_config.get("exclude", []),
            max_display=lang_config.get("max_display", 8),
            manual=lang_config.get("manual"),
        )

    def render_about_card(self) -> str:
        return about_card.render(
            profile=self.config.get("profile", {}),
            about=self.config.get("about", {}),
            theme=self.theme,
            galaxy_arms=self.galaxy_arms,
        )

    def render_projects_constellation(self) -> str:
        return projects_constellation.render(
            projects=self.projects,
            galaxy_arms=self.galaxy_arms,
            theme=self.theme,
        )
