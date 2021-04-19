from setuptools import setup

# Version
version = None
with open("./genopype/__init__.py", "r") as f:
    for line in f.readlines():
        line = line.strip()
        if line.startswith("__version__"):
            version = line.split("=")[-1].strip().strip('"')
assert version is not None, "Check version in genopype/__init__.py"

setup(name='genopype',
      version=version,
      description='Architecture for building creating pipelines',
      url='https://github.com/jolespin/genopype',
      author='Josh L. Espinoza',
      author_email='jespinoz@jcvi.org',
      license='BSD-3',
      packages=["genopype"],
      install_requires=[
      "pathlib2",
      "scandir",
      "soothsayer_utils",
      ],
)
