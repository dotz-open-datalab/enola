# -*- coding: utf-8 -*-

import time

import click

from enola.utils import read_product_config, run_cmd


# INTERNALS BEGIN


def _airflow_configs(configs):
    concat = list()

    for (section, obj) in configs.items():
        for (prop, value) in obj.items():
            concat.append('{}-{}={}'.format(section, prop, value))

    return ','.join(concat)


def _airflow_labels(labels):
    concat = list()

    for (key, value) in labels.items():
        concat.append('{}={}'.format(key, value))

    return ','.join(concat)


def _deploy(env, artifact):
    _TEMPLATE_IMPORT = [
        'gcloud composer environments storage {folder} import',
        '--environment {name}',
        '--location {location}',
        '--source ./composer/{folder}/{artifact}',
        '--project {project}'
    ]

    _TEMPLATE_RUN = [
        'gcloud composer environments run {name}',
        '--location {location}',
        '--project {project}',
        'list_dags'
    ]

    config = read_product_config('composer', env)

    run_cmd(_TEMPLATE_IMPORT, {
        'project': config['project'],
        'name': config['name'],
        'location': config['node-config']['location'],
        'folder': 'dags',
        'artifact': artifact
    })

    time.sleep(5)

    run_cmd(_TEMPLATE_RUN, {
        'project': config['project'],
        'name': config['name'],
        'location': config['node-config']['location']
    })


# INTERNALS END

# EXTERNALS BEGIN


@click.group()
def external_command():
    pass


@click.command()
@click.argument('env')
def build(env):
    _TEMPLATE = [
        'gcloud beta composer environments create {name}',
        '--project {project}',
        '--node-count {node-count}',
        '--location {location}',
        '--zone {zone}',
        '--machine-type {machine-type}',
        '--disk-size {disk-size}',
        '--tags {tags}',
        '--image-version {image-version}',
        '--python-version {python-version}',
        '--network {network}',
        '--subnetwork {subnetwork}',
        '--airflow-configs {airflow-configs}',
        '--labels {labels}',
        '--async'
    ]

    config = read_product_config('composer', env)

    run_cmd(_TEMPLATE, {
        'project': config['project'],
        'name': config['name'],
        'node-count': config['node-config']['count'],
        'location': config['node-config']['location'],
        'zone': config['node-config']['zone'],
        'machine-type': config['node-config']['machine-type'],
        'disk-size': config['node-config']['disk-size'],
        'tags': ','.join(config['node-config']['tags']),
        'image-version': config['node-config']['image'],
        'python-version': config['node-config']['python-version'],
        'network': config['network-config']['network'],
        'subnetwork': config['network-config']['subnetwork'],
        'airflow-configs': _airflow_configs(config['airflow-config-overrides']),
        'labels': _airflow_labels(config['labels'])
    })


@click.command()
@click.argument('env')
@click.argument('dagname')
def deploy_dag(env, dagname):
    filename = '{}.py'.format(dagname)
    _deploy(env, filename)


@click.command()
@click.argument('env')
@click.argument('dagnames', nargs=-1)
def deploy_dags(env, dagnames):
    for name in dagnames:
        filename = '{}.py'.format(name)
        _deploy(env, filename)


@click.command()
@click.argument('env')
@click.argument('name')
def deploy_lib(env, name):
    _deploy(env, name)


external_command.add_command(build)
external_command.add_command(deploy_dag, 'deploy-dag')
external_command.add_command(deploy_dags, 'deploy-dags')
external_command.add_command(deploy_lib, 'deploy-lib')


# EXTERNALS END
