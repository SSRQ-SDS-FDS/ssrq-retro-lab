from ssrq_retro_lab.train.data import OpenAIDataset, insert_text_into_template


def test_openai_dataset_to_dict():
    dataset = OpenAIDataset("Foo", "Bar", "Baz")
    assert dataset.to_dict() == {
        "messages": [
            {"role": "system", "content": "Foo"},
            {"role": "user", "content": "Bar"},
            {"role": "assistant", "content": "Baz"},
        ]
    }


def test_insert_text_into_template():
    input_template = "Foo [[text]]."
    input_text = "Bar"
    assert insert_text_into_template(input_template, input_text) == "Foo Bar."
