from src.templaterx import TemplaterX
from tests.helpers import template
from docxtpl import RichText, RichTextParagraph
from typing import cast
import docxtpl
import re


class RichTextTplDocxFactory:
    """
    Template: **richtext_tpl.docx**
    """
    @classmethod
    def build_rich_text(cls, tplx: TemplaterX) -> docxtpl.RichText:
        chunks: list[template.RichTextChunk] = [
            ("a rich text", {"style": "myrichtextstyle"}),
            (" with ", {}),
            ("some italic", {"italic": True}),
            (" and ", {}),
            ("some violet", {"color": "#ff00ff"}),
            (" and ", {}),
            ("some striked", {"strike": True}),
            (" and ", {}),
            ("some Highlighted", {"highlight": "#ffff00"}),
            (" and ", {}),
            ("some small", {"size": 14}),
            (" or ", {}),
            ("big", {"size": 60}),
            (" text.", {}),
            ("\nYou can add an hyperlink, here to ", {}),
            ("google", {"url_id": tplx.build_url_id("http://google.com")}),
            ("\nEt voilà ! ", {}),
            ("\n1st line", {}),
            ("\n2nd line", {}),
            ("\n3rd line", {}),
            ("\aA new paragraph : <cool>\a", {}),
            ("--- A page break here (see next page) ---\f", {}),
        ]

        underline_styles = [
            "single", "double", "thick", "dotted",
            "dash", "dotDash", "dotDotDash", "wave",
        ]

        chunks.extend(
            (f"\nUnderline : {ul} \n", {"underline": ul})
            for ul in underline_styles
        )

        chunks.extend([
            ("\nFonts :\n", {"underline": True}),
            ("Arial\n", {"font": "Arial"}),
            ("Courier New\n", {"font": "Courier New"}),
            ("Times New Roman\n", {"font": "Times New Roman"}),
            ("\n\nHere some", {}),
            ("superscript", {"superscript": True}),
            (" and some", {}),
            ("subscript", {"subscript": True}),
        ])

        rt = template.rich_text_from_chunks(chunks)

        return cast(RichText, template.rich_text_from_chunks(
            [("an example of ", {}), (rt, {})]
        ))

    @classmethod
    def assert_rich_text_is_rendered(cls, xml: str):
        RICH_PROPERTIES = [
            ("a rich text", "w:rStyle", {"w:val": "myrichtextstyle"}),
            ("some italic", "w:i", None),
            ("some violet", "w:color", {"w:val": "ff00ff"}),
            ("some striked", "w:strike", None),
            ("some Highlighted", "w:shd", {"w:fill": "ffff00"}),
            ("some small", "w:sz", {"w:val": "14"}),
            ("big", "w:sz", {"w:val": "60"}),
            ("superscript", "w:vertAlign", {"w:val": "superscript"}),
            ("subscript", "w:vertAlign", {"w:val": "subscript"}),
        ]

        UNDERLINES = [
            "single",
            "double",
            "thick",
            "dotted",
            "dash",
            "dotDash",
            "dotDotDash",
            "wave",
        ]

        FONTS = [
            "Arial",
            "Courier New",
            "Times New Roman",
        ]

        assert re.search(
            r'<w:hyperlink\b[^>]*>.*?<w:t[^>]*>google</w:t>',
            xml, re.DOTALL
        )

        for line in [
            "You can add an hyperlink, here to ",
            "Et voilà ! ",
            "1st line",
            "2nd line",
            "3rd line",
        ]:
            assert f">{line}<" in xml

        assert r"A new paragraph : &lt;cool&gt;" in xml
        assert '<w:br w:type="page"/>' in xml

        for text, tag, attrs in RICH_PROPERTIES:
            template.assert_text_has_property(
                xml,
                text,
                prop_tag=tag,
                prop_attrs=attrs,
            )

        for ul in UNDERLINES:
            template.assert_text_has_property(
                xml,
                f"Underline : {ul}",
                prop_tag="w:u",
                prop_attrs={"w:val": ul},
            )

        for font in FONTS:
            template.assert_text_has_property(
                xml,
                font,
                prop_tag="w:rFonts",
                prop_attrs={
                    "w:ascii": font,
                    "w:hAnsi": font,
                    "w:cs": font,
                },
            )


class RichtextParagraphTplDocxFactory:
    """
    Template: **richtext_paragraph_tpl.docx**
    """
    @classmethod
    def build_richtext_paragraph(cls) -> RichTextParagraph:
        rtp = RichTextParagraph()

        paragraph_chunks: list[template.RichTextChunk] = [
            (
                "The rich text paragraph function allows paragraph styles to be added to text",
                {"parastyle": "myrichparastyle"},
            ),
            (
                "Any built in paragraph style can be used",
                {"parastyle": "IntenseQuote"}
            ),
            (
                "or you can add your own, unlocking all style options",
                {"parastyle": "createdStyle"},
            ),
            (
                "To use, just create a style in your template word doc with the formatting you want "
                "and call it in the code.",
                {"parastyle": "normal"},
            ),
            ("This allows for the use of", {}),
            ("custom bullet\apoints", {"parastyle": "SquareBullet"}),
            ("Numbered Bullet Points", {"parastyle": "BasicNumbered"}),
            ("and Alpha Bullet Points.", {
             "parastyle": "alphaBracketNumbering"}),
            ("You can", {"parastyle": "normal"}),
            ("set the", {"parastyle": "centerAlign"}),
            ("text alignment", {"parastyle": "rightAlign"}),
            (
                "as well as the spacing between lines of text. Like this for example, "
                "this text has very tight spacing between the lines.\aIt also has no space between "
                "paragraphs of the same style.",
                {"parastyle": "TightLineSpacing"},
            ),
            (
                "Unlike this one, which has extra large spacing between lines for when you want to "
                "space things out a bit or just write a little less.",
                {"parastyle": "WideLineSpacing"},
            ),
            (
                "You can also set the background colour of a line.",
                {"parastyle": "LineShadingGreen"},
            ),
        ]

        template.rich_text_from_chunks(paragraph_chunks, base=rtp)

        richtext_chunks: list[template.RichTextChunk] = [
            ("This works with ", {}),
            ("Rich ", {"bold": True}),
            ("Text ", {"italic": True}),
            ("Strings", {"underline": "single"}),
            (" too.", {}),
        ]

        rt = template.rich_text_from_chunks(richtext_chunks)

        rtp.add(rt, parastyle="SquareBullet")

        return rtp

    @classmethod
    def assert_richtext_paragraph_is_rendered(cls, xml: str):
        PARAGRAPH_STYLES = [
            (
                "The rich text paragraph function allows paragraph styles to be added to text",
                "myrichparastyle",
            ),
            (
                "Any built in paragraph style can be used",
                "IntenseQuote",
            ),
            (
                "or you can add your own, unlocking all style options",
                "createdStyle",
            ),
            (
                "To use, just create a style in your template word doc with the formatting you want "
                "and call it in the code.",
                "normal",
            ),
            ("custom bullet", "SquareBullet"),
            ("Numbered Bullet Points", "BasicNumbered"),
            ("and Alpha Bullet Points.", "alphaBracketNumbering"),
            ("You can", "normal"),
            ("set the", "centerAlign"),
            ("text alignment", "rightAlign"),
            (
                "as well as the spacing between lines of text. Like this for example, "
                "this text has very tight spacing between the lines.",
                "TightLineSpacing",
            ),
            (
                "Unlike this one, which has extra large spacing between lines for when you want to "
                "space things out a bit or just write a little less.",
                "WideLineSpacing",
            ),
            (
                "You can also set the background colour of a line.",
                "LineShadingGreen",
            ),
        ]

        for text, style in PARAGRAPH_STYLES:
            template.assert_text_has_property(
                xml,
                text,
                prop_tag="w:pStyle",
                prop_attrs={"w:val": style},
            )

        RICH_RUN_PROPERTIES = [
            ("Rich ", "w:b", None),
            ("Text ", "w:i", None),
            ("Strings", "w:u", {"w:val": "single"}),
        ]

        for text, tag, attrs in RICH_RUN_PROPERTIES:
            template.assert_text_has_property(
                xml,
                text,
                prop_tag=tag,
                prop_attrs=attrs,
            )

        for text in [
            "This allows for the use of",
            "This works with ",
            " too.",
        ]:
            assert f">{text}<" in xml
