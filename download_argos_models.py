import os

os.environ["ARGOS_PACKAGES_DIR"] = "./data/argos-translate/packages"

import argostranslate.package

from_code = "en"
to_code = "de"

argostranslate.package.update_package_index()
available_packages = argostranslate.package.get_available_packages()
available_package = list(
    filter(
        lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
    )
)[0]
download_path = available_package.download()
argostranslate.package.install_from_path(download_path)
