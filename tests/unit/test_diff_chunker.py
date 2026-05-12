from app.services.diff_chunker import chunk_patch


def test_chunk_patch_returns_chunks():
    patch = """@@ -1,3 +1,4 @@
 def hello():
+    print("hello")
     return True
"""
    chunks = chunk_patch("app/main.py", patch, max_lines=10)


    assert len(chunks) == 1
    assert chunks[0].file_path == "app/main.py"
    assert chunks[0].chunk_index == 0
    assert 'print("hello")' in chunks[0].content


def test_chunk_patch_splits_large_patch():
    patch = "@@ -1,100 +1,100 @@\n" + "\n".join(
        [f"+line {i}" for i in range(200)]
    )

    chunks = chunk_patch("app/large.py", patch, max_lines=50)
    print("chunks:", chunks)

    assert len(chunks) > 1
    assert chunks[0].chunk_index == 0
    assert chunks[1].chunk_index == 1


def test_empty_patch_returns_empty_list():
    chunks = chunk_patch("app/main.py", None)

    assert chunks == []