from ssrq_retro_lab.pipeline.parser.html_to_article import (
    remove_header_from_pages,
    collect_article_nodes_from_pages,
)
from ssrq_retro_lab.pipeline.components.text_extractor import (
    TextExtractor,
    ExtractionInput,
)
from parsel import Selector


def test_collect_article_nodes_from_pages():
    html_page_one = """<div>
    <p style="top:74.9pt;left:385.9pt;line-height:10.0pt">
        foo
    </p>
    <p style="top:99.0pt;left:93.5pt;line-height:10.0pt">
        <i>
            <span style="font-family:Times New Roman,serif;font-size:10.0pt">1276 April 14.</span>
        </i>
    </p>
    <p style="top:111.9pt;left:73.3pt;line-height:10.0pt">
        <span style="font-family:Times New Roman,serif;font-size:10.0pt">14. </span>
        <i>
            <span style="font-family:Times New Roman,serif;font-size:10.0pt">Zehnten der Chamer Kirche</span>
        </i>
    </p></div>"""
    html_page_two = """<div>
    <p style="top:511.6pt;left:92.9pt;line-height:10.0pt">
		<span style="font-family:Times New Roman,serif;font-size:10.0pt">orten diser kilchhöri nimpt das Frowenmünster zwen teil und die </span>
	</p>
	<p style="top:524.7pt;left:92.5pt;line-height:10.0pt">
		<span style="font-family:Times New Roman,serif;font-size:10.0pt">probstig den dritteil, usgenomen die widern.</span>
	</p>
	<p style="top:540.6pt;left:77.5pt;line-height:6.0pt">
		<span style="font-family:Times New Roman,serif;font-size:6.0pt">35 </span>
		<span style="font-family:Times New Roman,serif;font-size:10.0pt">Die widern am Len soll 2 schwin usrichten, geltend 1 1 b, das Nider- </span>
	</p>
	<p style="top:550.5pt;left:92.4pt;line-height:10.0pt">
		<span style="font-family:Times New Roman,serif;font-size:10.0pt">len 4 s.</span>
	</p>
	<p style="top:563.2pt;left:92.9pt;line-height:10.0pt">
		<span style="font-family:Times New Roman,serif;font-size:10.0pt">Die widern ab der Furen gilt 10 viertel kernen.</span>
	</p>
	<p style="top:575.9pt;left:93.0pt;line-height:10.0pt">
		<span style="font-family:Times New Roman,serif;font-size:10.0pt">Item Wimmans acker 5 viertel kernen.</span>
	</p>
	<p style="top:588.5pt;left:93.0pt;line-height:10.0pt">
		<span style="font-family:Times New Roman,serif;font-size:10.0pt">Item die widern in Büsickon in der kilcheri ze Barr 2 viertel kernen.</span>
	</p></div>"""
    html_page_three = """<div>
    <p style="top:343.7pt;left:77.5pt;line-height:6.0pt">
		<span style="font-family:Times New Roman,serif;font-size:6.0pt">20 </span>
	</p>
	<p style="top:342.1pt;left:93.5pt;line-height:8.0pt">
		<b>
			<i>
				<span style="font-family:Times New Roman,serif;font-size:8.0pt">(Hausen ZH), 8 Meierskappel L U ,9 Hausen ZH,</span>
			</i>
		</b>
	</p>
	<p style="top:356.7pt;left:94.1pt;line-height:10.0pt">
		<i>
			<span style="font-family:Times New Roman,serif;font-size:10.0pt">(1278-1280 und um 1285)</span>
		</i>
	</p>
	<p style="top:369.9pt;left:73.4pt;line-height:10.0pt">
		<span style="font-family:Times New Roman,serif;font-size:10.0pt">15. </span>
		<i>
			<span style="font-family:Times New Roman,serif;font-size:10.0pt">Zinsrodel Fraumünster Zürich</span>
		</i>
	</p>
    </div>"""

    pages = (html_page_one, html_page_two, html_page_three)

    result = collect_article_nodes_from_pages(pages, 14, 15)

    assert result.is_ok()

    unwrapped_result = result.unwrap()

    assert isinstance(unwrapped_result, tuple)

    first_node = unwrapped_result[0]

    assert "14." in first_node.get()

    last_node = unwrapped_result[-1]

    assert "Hausen ZH" in last_node.get()

    assert len(unwrapped_result) == 10


def test_collect_article_nodes_from_pages_against_pdf():
    extraction_result = TextExtractor().invoke(ExtractionInput(793, 525, 525)).unwrap()

    result = collect_article_nodes_from_pages(extraction_result["pages"], 793, 794)

    assert result.is_ok()

    unwrapped_result = result.unwrap()

    assert isinstance(unwrapped_result, tuple)

    assert len(unwrapped_result) == 6


def test_remove_header_from_pages():
    html = """<div id="page0" style="width:485.8pt;height:737.3pt">
	<p style="top:75.3pt;left:92.7pt;line-height:8.5pt">
		<span style="font-family:Sylfaen,serif;font-size:8.5pt">A. Die geistlichen Grundherr schäften im Mittelalter • 8-14</span>
	</p>
	<p style="top:74.9pt;left:385.9pt;line-height:10.0pt">
		<b>
			<span style="font-family:Times New Roman,serif;font-size:10.0pt">47</span>
		</b>
	</p>
	<p style="top:99.0pt;left:93.5pt;line-height:10.0pt">
		<i>
			<span style="font-family:Times New Roman,serif;font-size:10.0pt">1276 April 14.</span>
		</i>
	</p>
	<p style="top:111.9pt;left:73.3pt;line-height:10.0pt">
		<span style="font-family:Times New Roman,serif;font-size:10.0pt">14. </span>
		<i>
			<span style="font-family:Times New Roman,serif;font-size:10.0pt">Zehnten der Chamer Kirche</span>
		</i>
	</p></div>"""

    pages = (html, html, html)

    result = remove_header_from_pages(pages)

    assert result.is_ok()

    for page in result.unwrap():
        assert len(Selector(page, type="xml").xpath("//p")) == 2
