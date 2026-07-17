from setuptools import setup, find_packages

setup(
    name="target-mock",
    version="0.1.0",
    description="A Singer target for mock data processing with state management",
    author="hotglue",
    author_email="support@hotglue.xyz",
    url="https://github.com/hotglue/target-mock",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14"
    ],
    keywords=["ELT", "Singer", "Target", "Mock"],
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "hotglue-singer-sdk>=1.0.40",
        "requests>=2.25.1",
    ],
    extras_require={
        "dev": [
            "pytest>=6.2.5",
            "pytest-cov>=2.12.0",
            "black>=21.9b0",
            "flake8>=3.9.2",
            "mypy>=0.910",
            "isort>=5.10.1",
        ]
    },
    entry_points={
        "console_scripts": [
            "target-mock=target_mock.target:TargetMock.cli",
        ],
    },
    python_requires=">=3.10",
) 