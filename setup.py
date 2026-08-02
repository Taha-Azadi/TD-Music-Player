from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="td-music-player",
    version="1.0.0",
    author="Taha Azadi",
    author_email="",
    description="A modern, professional music player built with Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Taha-Azadi/TD-Music-Player",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Multimedia :: Sound/Audio :: Players",
    ],
    python_requires=">=3.8",
    install_requires=[
        "customtkinter>=5.2.0",
        "pygame>=2.5.0",
        "Pillow>=10.0.0",
        "mutagen>=1.47.0",
    ],
    extras_require={
        "tray": ["pystray>=0.19.0"],
        "dev": ["pytest>=7.0", "black>=22.0", "flake8>=4.0"],
    },
    entry_points={
        "console_scripts": [
            "td-music=td_music_player.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "td_music_player": ["assets/*"],
    },
)
