from setuptools import setup

setup(
    name='modui',
    version='1.0.0',
    author='metarooster',
    license='MIT',
    python_requires='>=3.7',
    setup_requires=['cmake', 'requests'],
    install_requires=['gradio']
)