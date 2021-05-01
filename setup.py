import setuptools
import fastapi_mail
with open("README.md", "r") as fh:
    long_description = fh.read()

test_dependencies = ["pytest", "pytest-asyncio", "pytest-mock", "pytest-cov"]

setuptools.setup(
    name="fastapi-mail",
    version=fastapi_mail.__version__,
    author="Sabuhi Shukurov",
    author_email="sabuhi.shukurov@gmail.com",
    description="Simple lightwigh mail sending for FastApi",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    url="https://github.com/sabuhish/fastapi-mail",
    install_requires=["fastapi>=0.61.2",'jinja2>=2.11.2',"aiosmtplib>=1.1.5","python-multipart>=0.0.5", "pydantic>=1.7.1","email-validator>=1.1.1","aioredis>=1.3.1","httpx>=0.16.1","blinker>=1.4","fakeredis>=1.4.5"],
    tests_require=test_dependencies,
    test_suite="tests",
    dependency_links=["https://github.com/cole/aiosmtplib/archive/e8e5ea5acb959f374909dd7961fab865473dbc80.zip#egg=aiosmtplib-1.1.4+gite8e5ea5"],
    extras_require={
        'testing':test_dependencies,
        "docs":[
            "mkdocs>=1.1.2",
            "mkdocs-material>=6.1.5",
            "mkdocs-markdownextradata-plugin>=0.1.9"
            ],
        "extra":[
            "blinker>=1.4"
        ]
        
    },
    platforms=['any'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)


