from setuptools import find_packages, setup

package_name = 'coach_pupper'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ubuntu',
    maintainer_email='ubuntu@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': ['service = coach_pupper.service_go_pupper:main', 
        'client = coach_pupper.client_go_pupper:main', 
        'pupper_game = coach_pupper.PupperGame:main'
        ],
    },
)
