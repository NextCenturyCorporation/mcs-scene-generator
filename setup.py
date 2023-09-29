import setuptools

with open('README.md', 'r') as readme_file:
    long_description = readme_file.read()


setuptools.setup(
    name='mcs_scene_generator',
    version=1.12,
    maintainer='Next Century, a wholly owned subsidiary of CACI',
    maintainer_email='mcs-ta2@machinecommonsense.com',
    url='https://github.com/NextCenturyCorporation/mcs-scene-generator/',
    description=('Machine Common Sense Interactive Learning Environment and '
                 'Hypercube Scene Generators'),
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    license='Apache-2',
    python_requires=">=3.8",
    packages=setuptools.find_packages(),
    install_requires=[
        'machine-common-sense>=0.7.1',
        'pyyaml>=5.3.1',
        'shapely>=1.7.0'
    ],
    entry_points={
        'console_scripts': [
            'generate_public_scenes=generate_public_scenes:main',
            'ile=ile:main'
        ]
    }

)
