from ssrq_retro_lab.utils.split_exports import split_content


def test_split_content():
    content = """Foo bar
    bar baz

    bar baz

    bar foo"""
    expected_result = ["Foo bar\nbar baz", "bar baz", "bar foo"]
    assert split_content(content) == expected_result
