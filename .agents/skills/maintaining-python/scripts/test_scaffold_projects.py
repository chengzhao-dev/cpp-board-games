#!/usr/bin/env python3
"""验证工程脚手架布局、模板渲染和防覆盖行为。"""

from contextlib import redirect_stdout
import importlib.util
import io
from pathlib import Path
import shutil
import sys

ROOT = Path(__file__).resolve().parents[4]
sys.dont_write_bytecode = True
SCAFFOLD = (
    ROOT
    / ".agents"
    / "skills"
    / "maintaining-python"
    / "scripts"
    / "scaffold"
    / "init_project.py"
)
sys.path.insert(0, str(ROOT / ".agents" / "skills" / "maintaining-python" / "scripts"))
from temp_paths import temp_dir  # noqa: E402


def load_scaffold():
    spec = importlib.util.spec_from_file_location("init_project", SCAFFOLD)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def create_project(module, case_root, name, layout):
    sys.argv = [
        "init_project.py",
        "--name",
        name,
        "--dir",
        str(case_root),
        "--layout",
        layout,
    ]
    with redirect_stdout(io.StringIO()):
        return module.main()


def assert_target_comment(text, command, comment):
    lines = text.splitlines()
    assert command in lines
    index = lines.index(command)
    assert lines[index - 1] == comment


def main():
    module = load_scaffold()
    assert module.to_cmake_project_name("multi_file-project") == "MultiFileProject"
    test_root = temp_dir("scaffold-tests")
    case_root = test_root / "cases"
    if case_root.exists():
        assert test_root.resolve() in case_root.resolve().parents
        shutil.rmtree(case_root)
    case_root.mkdir(parents=True)

    single = case_root / "single-project"
    assert create_project(module, case_root, single.name, "single") == 0
    for rel in (
        "main.cpp",
        "CMakeLists.txt",
        "build-and-run.sh",
        ".clang-format",
        ".clang-tidy",
        ".clangd",
        ".vscode/settings.json",
        ".vscode/extensions.json",
    ):
        assert (single / rel).is_file(), rel
    single_cmake = (single / "CMakeLists.txt").read_text(encoding="utf-8")
    assert "{{PROJECT_NAME}}" not in single_cmake
    assert "{{CMAKE_PROJECT_NAME}}" not in single_cmake
    assert "project(SingleProject LANGUAGES CXX)" in single_cmake
    assert single_cmake.splitlines()[0] == "# 构建 SingleProject 可执行目标。"
    assert_target_comment(
        single_cmake,
        "add_executable(app main.cpp)",
        "# 创建 app 可执行目标。",
    )
    assert (single / "main.cpp").read_text(encoding="utf-8").splitlines()[0] == (
        "// 程序入口：向标准输出打印问候。"
    )
    single_script = (single / "build-and-run.sh").read_text(encoding="utf-8").splitlines()
    assert single_script[0] == "#!/usr/bin/env bash"
    assert single_script[1] == "# 配置、构建并运行当前 CMake 项目。"

    multi = case_root / "multi-project"
    assert create_project(module, case_root, multi.name, "multi") == 0
    for rel in (
        "include/greeting.h",
        "src/greeting.cpp",
        "src/main.cpp",
        "CMakeLists.txt",
        "build-and-run.sh",
        ".clang-format",
        ".vscode/settings.json",
    ):
        assert (multi / rel).is_file(), rel
    cmake = (multi / "CMakeLists.txt").read_text(encoding="utf-8")
    assert "{{PROJECT_NAME}}" not in cmake
    assert "{{CMAKE_PROJECT_NAME}}" not in cmake
    assert "project(MultiProject LANGUAGES CXX)" in cmake
    assert cmake.splitlines()[0] == "# 构建 MultiProject 可执行目标。"
    assert "add_executable(app src/main.cpp src/greeting.cpp)" in cmake
    assert_target_comment(
        cmake,
        "add_executable(app src/main.cpp src/greeting.cpp)",
        "# 创建 app 可执行目标，并列出参与构建的源文件。",
    )
    assert "target_include_directories(app PRIVATE include)" in cmake
    assert (multi / "include/greeting.h").read_text(
        encoding="utf-8"
    ).splitlines()[0] == "// 问候接口：声明 MakeGreeting()，供其他源文件调用。"
    assert (multi / "src/greeting.cpp").read_text(
        encoding="utf-8"
    ).splitlines()[0] == "// 实现 greeting.h 中声明的 MakeGreeting()。"
    assert (multi / "src/main.cpp").read_text(
        encoding="utf-8"
    ).splitlines()[0] == "// 程序入口：调用 MakeGreeting() 并输出结果。"

    library_cases = (
        (
            "static-library",
            "StaticLibrary",
            "STATIC",
            "ARCHIVE",
        ),
        (
            "shared-library",
            "SharedLibrary",
            "SHARED",
            "LIBRARY",
        ),
    )
    for name, project_name, library_type, output_kind in library_cases:
        library = case_root / name
        assert create_project(module, case_root, name, name) == 0
        for rel in (
            "greeting/include/greeting.h",
            "greeting/src/greeting.cpp",
            "greeting/CMakeLists.txt",
            "main.cpp",
            "CMakeLists.txt",
            "build-and-run.sh",
            ".clang-format",
            ".vscode/settings.json",
        ):
            assert (library / rel).is_file(), f"{name}/{rel}"
        library_cmake = (library / "CMakeLists.txt").read_text(encoding="utf-8")
        module_cmake = (library / "greeting/CMakeLists.txt").read_text(encoding="utf-8")
        assert "{{CMAKE_PROJECT_NAME}}" not in library_cmake
        assert f"project({project_name} LANGUAGES CXX)" in library_cmake
        assert "add_subdirectory(greeting)" in library_cmake
        assert "add_executable(app main.cpp)" in library_cmake
        assert_target_comment(
            library_cmake,
            "add_executable(app main.cpp)",
            (
                "# 创建 app 可执行目标，并在链接阶段使用 greeting 静态库。"
                if library_type == "STATIC"
                else "# 创建 app 可执行目标，并在链接阶段记录对 greeting 动态库的依赖。"
            ),
        )
        assert "add_library(greeting" not in library_cmake
        assert f"add_library(greeting {library_type} src/greeting.cpp)" in module_cmake
        assert "target_include_directories(greeting PUBLIC include)" in module_cmake
        assert "target_link_libraries(app PRIVATE greeting)" in library_cmake
        assert f"CMAKE_{output_kind}_OUTPUT_DIRECTORY ${{CMAKE_BINARY_DIR}}/lib" in library_cmake
        assert "CompilationDatabase: build" in (library / ".clangd").read_text(
            encoding="utf-8"
        )
        assert not (library / "include").exists()
        assert not (library / "src").exists()
        assert not (library / "app").exists()
        assert (library / "greeting/include/greeting.h").read_text(
            encoding="utf-8"
        ).splitlines()[0] == "// 问候库接口：声明 MakeGreeting()，供 app 调用。"
        assert (library / "main.cpp").read_text(
            encoding="utf-8"
        ).splitlines()[0] == "// 程序入口：调用库提供的 MakeGreeting() 并输出结果。"
        if name == "shared-library":
            assert 'set_target_properties(app PROPERTIES BUILD_RPATH "$ORIGIN/../lib")' in library_cmake

    compatible = case_root / "complete-project"
    assert create_project(module, case_root, compatible.name, "complete") == 0
    assert (compatible / "main.cpp").is_file()
    assert (compatible / "build-and-run.sh").is_file()
    assert not (compatible / "src").exists()
    assert "project(CompleteProject LANGUAGES CXX)" in (
        compatible / "CMakeLists.txt"
    ).read_text(encoding="utf-8")

    bare = case_root / "bare-project"
    assert create_project(module, case_root, bare.name, "bare") == 0
    assert (bare / "main.cpp").is_file()
    assert not (bare / "CMakeLists.txt").exists()

    assert create_project(module, case_root, single.name, "single") == 1
    print("PASS scaffold projects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
