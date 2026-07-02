import pytchbuild.tutorialcompiler.fromgitrepo.tutorial_markdown as TM


class TestShortcodeParsing:
    def test_shortcode(self, tutorial_md_text):
        if tutorial_md_text.startswith("Working copy"):
            return
        soup = TM.soup_from_markdown_text(tutorial_md_text)
        all_maybe_slugs = [elt.get("data-slug", None) for elt in soup.find_all()]
        all_mentioned_slugs = [s for s in all_maybe_slugs if s is not None]
        assert all_mentioned_slugs == ["import-pytch", "add-Alien-skeleton"]

    def test_ordered_commit_slugs_in_soup(self, tutorial_md_text):
        if tutorial_md_text.startswith("Working copy"):
            return
        soup = TM.soup_from_markdown_text(tutorial_md_text)
        ordered_commit_slugs = TM.ordered_commit_slugs_in_soup(soup)
        assert ordered_commit_slugs == ["import-pytch", "add-Alien-skeleton"]

    def test_scratchblocks_code(self, tutorial_md_text):
        if tutorial_md_text.startswith("Working copy"):
            return
        soup = TM.soup_from_markdown_text(tutorial_md_text)
        all_code_elts = soup.find_all("code", "language-scratch")
        all_code_texts = [elt.get_text() for elt in all_code_elts]
        assert all_code_texts == ["go to x: [0] y: [120]\n"]


class TestCreditsParsing:
    def _basenames(self, credits_text):
        return [
            credit.asset_basenames
            for credit in TM.AssetListCredit.list_from_credits_text(credits_text)
        ]

    def test_single_and_grouped_basenames(self):
        text = (
            "# Credits\n\n"
            "Some intro prose which is ignored.\n\n"
            "- `alien.png` — Drawn by A. Author.\n"
            "- `small-blue.png`, `small-red.png` — Made by us.\n"
        )
        assert self._basenames(text) == [
            ["alien.png"],
            ["small-blue.png", "small-red.png"],
        ]

    def test_ignores_non_credit_bullets_and_prose(self):
        text = (
            "- `real.png` — A credit.\n"
            "- Just a prose bullet, not a credit.\n"
            "- **bold** then `late.png` — leading content is not code.\n"
        )
        assert self._basenames(text) == [["real.png"]]

    def test_ignores_headings_and_fenced_code(self):
        text = (
            "## Project assets\n\n"
            "- `real.png` — A credit.\n\n"
            "```\n"
            "- `fenced.png` — inside a fenced code block, ignored\n"
            "```\n"
        )
        assert self._basenames(text) == [["real.png"]]

    def test_credit_body_is_html(self):
        text = "- `snd.mp3` — Sound by [B](https://example.com/).\n"
        [credit] = TM.AssetListCredit.list_from_credits_text(text)
        assert credit.asset_basenames == ["snd.mp3"]
        li = credit.credit_li
        assert li.name == "li"
        # The backtick-quoted basename survives as a leading <code>, and the
        # body's markdown is parsed to HTML (here, a link).
        assert li.find("code").get_text() == "snd.mp3"
        assert li.find("a")["href"] == "https://example.com/"

    def test_leading_code_texts_helper(self):
        soup = TM.plain_soup_from_markdown_text(
            "- `a.png`, `b.png` — body\n- plain bullet\n"
        )
        lis = soup.find_all("li")
        assert TM.leading_code_texts(lis[0]) == ["a.png", "b.png"]
        assert TM.leading_code_texts(lis[1]) is None
