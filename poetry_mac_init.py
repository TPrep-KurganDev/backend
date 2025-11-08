import os
import subprocess
import sys
import tomllib
from typing import Iterable


class PipPackage:
    def __init__(
        self, name: str, brew_deps: list[str] | None = None, include_brew: bool = False, build_ext: bool = False
    ) -> None:
        self.name = name
        self._brew_deps = brew_deps
        self._include_brew = include_brew
        self._build_ext = build_ext

    def _brew_upgrade(self) -> None:
        deps = []
        if self._brew_deps is not None:
            deps = self._brew_deps

        subprocess.check_call(["brew", "upgrade", *deps])

    def _get_global_options(self) -> list[str]:
        global_options = []

        if self._build_ext:
            global_options.append('build_ext')

        if self._brew_deps is not None:
            for dep in self._brew_deps:
                prefix = self._brew_prefix(dep)
                global_options.append(f'-I{os.path.join(prefix, "include", "")}')
                global_options.append(f'-L{os.path.join(prefix, "lib", "")}')

        return global_options

    def install(self, version: str) -> None:
        self._brew_upgrade()
        self._pip_install(version, self._get_global_options())

    def _brew_prefix(self, brew_package_name: str) -> str:
        return subprocess.check_output(['brew', '--prefix', brew_package_name]).decode().strip()

    def _pip_install(self, version: str, global_options: Iterable[str] | None = None) -> None:
        args: list[str] = []

        if global_options is not None:
            args.extend(f'-C--global-option={opt}' for opt in global_options)

        args.append(f"{self.name}=={version}")

        subprocess.check_call([sys.executable, "-m", "pip", "install", *args])


class PipPackageLxml(PipPackage):
    def __init__(self) -> None:
        super().__init__('lxml', ["libxslt", "libxml2"])

    def _get_global_options(self) -> list[str]:
        return [
            f"--with-xslt-config={self._brew_prefix('libxslt')}/bin/xslt-config",
            f"--with-xml2-config={self._brew_prefix('libxml2')}/bin/xml2-config",
        ]


class MacPackageInfo:
    def __init__(self, *packages: PipPackage):
        self._packages: dict[str, PipPackage] = {}

        for each in packages:
            self._packages[each.name] = each

    def __getitem__(self, key: str) -> PipPackage | None:
        return self._packages.get(key)


mac_packages = MacPackageInfo(
    PipPackageLxml()
)

if __name__ == '__main__':
    with open('poetry.lock', 'rb') as f:
        poetry_lock = tomllib.load(f)

    for package_lock in poetry_lock['package']:
        if (package := mac_packages[package_lock['name']]) is not None:
            print('Workaround for', package.name)
            package.install(package_lock['version'])
