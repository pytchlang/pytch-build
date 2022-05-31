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
        print(soup)
        all_maybe_slugs = [elt.get_text() for elt in soup.find_all('code')]
        print(all_maybe_slugs)
        all_mentioned_slugs = [s for s in all_maybe_slugs if s is not None]
        assert all_mentioned_slugs == ['go to x: [0] y: [120]\n']
        
