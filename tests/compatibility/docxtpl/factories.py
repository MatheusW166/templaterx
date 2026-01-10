from src.templaterx import TemplaterX
from tests.helpers import template
import docxtpl
import re


class RichTextTplDocxFactory:
    """
    This class builds a predefined RichText object for
    tempalte "richtext_tpl.docx" and provides assertions 
    to check that its properties are correctly rendered 
    in the final XML.
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

        return template.rich_text_from_chunks(
            [("an example of ", {}), (rt, {})]
        )

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
