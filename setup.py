import setuptools
from machine_common_sense import _version as version

with open('README.md', 'r') as readme_file:
    long_description = readme_file.read()


setuptools.setup(
    name='mcs_scene_generator',
    version=version.__version__,
    maintainer='Next Century, a wholly owned subsidiary of CACI',
    maintainer_email='mcs-ta2@machinecommonsense.com',
    url='https://github.com/NextCenturyCorporation/mcs-scene-generator/',
    description=('Machine Common Sense Ideal Learning Environment and '
                 'Scene Generator'),
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
        'machine-common-sense>=0.5.5',
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
