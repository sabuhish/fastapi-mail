import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fastapi-mail",
    version=__import__("fastapi_mail").VERSION,
    author="Sabuhi Shukurov",
    author_email="sabuhi.shukurov@gmail.com",
    description="Simple lightwigh mail sending for FastApi",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    url="https://github.com/sabuhish/fastapi-mail",
    install_requires=["fastapi>=0.61.2",'jinja2>=2.11.2',"aiosmtplib>=1.1.4","python-multipart>=0.0.5", "pydantic>=1.7.1","email-validator>=1.1.1"],
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
