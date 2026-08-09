from gitbloom.scanner import BloomBlock, find_bloom_blocks, format_blocks, prune_trailing_blocks


def test_list_single_block_detects_trailing_comments():
    lines = [
        "print('hello')\n",
        "\n",
        "# deployed: 2026-09-01\n",
        "# TODO cleanup\n",
        "# END COMMENT\n",
    ]
    blocks = find_bloom_blocks(lines)
    assert len(blocks) == 1
    assert blocks[0].start == 2
    assert blocks[0].end == 4
    assert blocks[0].body == "# deployed: 2026-09-01\n# TODO cleanup\n# END COMMENT\n"


def test_list_multiple_blocks_splits_on_blank():
    lines = [
        "x = 1\n",
        "\n",
        "# 2026-09-01\n",
        "# first\n",
        "\n",
        "# 2026-10-01\n",
        "# second\n",
        "# END DISCUSSION\n",
    ]
    blocks = find_bloom_blocks(lines)
    assert len(blocks) == 2
    assert blocks[0].start == 5
    assert blocks[1].start == 2


def test_list_empty_file():
    assert find_bloom_blocks([]) == []


def test_prune_removes_all_with_keep_zero():
    lines = [
        "print('code')\n",
        "\n",
        "# 2026-08-01\n",
        "# older\n",
        "\n",
    ]
    pruned = prune_trailing_blocks(lines, keep=0)
    assert pruned == ["print('code')\n"]


def test_prune_removes_oldest_when_multiple_blocks():
    lines = [
        "print('hello')\n",
        "\n",
        "# 2026-08-01\n",
        "# older\n",
        "\n",
        "# 2026-10-01\n",
        "# newer\n",
        "\n",
    ]
    pruned = prune_trailing_blocks(lines, keep=1)
    assert pruned == [
        "print('hello')\n",
        "\n",
        "\n",
        "# 2026-10-01\n",
        "# newer\n",
    ]


def test_prune_negative_keep_raises():
    try:
        prune_trailing_blocks(["# comment\n"], keep=-1)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")


def test_format_text_renders_blocks():
    blocks = [
        BloomBlock(start=2, end=4, body="# 2026-09-01\n# note\n", markers=("2026-09-01",))
    ]
    rendered = format_blocks(blocks, output_format="text")
    assert "Block from line 3-4:" in rendered
    assert "2026-09-01" in rendered


def test_format_json_renders_blocks():
    blocks = [BloomBlock(start=0, end=1, body="# note\n", markers=())]
    rendered = format_blocks(blocks, output_format="json")
    assert rendered.startswith("[")
    assert '"markers": []' in rendered
    assert '"body": "# note' in rendered
