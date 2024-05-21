import click
from fetch_info import *
from update_version import *
import yaml


class MyDumper(yaml.Dumper):
    def write_line_break(self, data=None):
        super().write_line_break(data)
        # Check if we are in the app list
        if len(self.indents) == 3:  # This level corresponds to items under `app`
            super().write_line_break()


@click.group()
def cli():
    """A command line tool for getting info and updating kubernetes deployment image."""


@cli.command()
@click.option('--file', '-f', required=True, type=click.File(encoding='utf-8'), default='update-version.yaml',
              help='YAML file default is update-version.yaml')
def get_info(file):
    data = yaml.safe_load(file)
    cluster = data[0]["cluster"]
    namespace = data[0]["namespace"]
    apps_info = data[1].get('app')
    out_info(cluster, namespace, apps_info, "get")


@cli.command()
@click.option('--file', '-f', required=True, type=click.File(encoding='utf-8'), default='update-version.yaml',
              help='YAML file default is update-version.yaml')
def update_image(file):
    data = yaml.safe_load(file)
    cluster = data[0]["cluster"]
    namespace = data[0]["namespace"]
    apps_info = data[1].get('app')
    out_info(cluster, namespace, apps_info, "update")

    registry_name = data[0]["registry"]

    for app_info in apps_info:
        if app_info.get('isUpdate') == True:
            for app_name in app_info.get('appList'):
                new_image = f"{registry_name}/{app_info.get('imageName')}:{app_info.get('version')}"
                update_deployment_image(cluster, namespace, app_name, new_image)


@cli.command()
@click.option('--file', '-f', required=True, type=str, default='update-version.yaml',
              help='YAML file default is update-version.yaml')
def rest_info(file):
    with open(file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)

    # 递归函数来遍历和更新 isUpdate 字段
    def update_flag(obj):
        if isinstance(obj, list):
            for item in obj:
                update_flag(item)
        elif isinstance(obj, dict):
            for key, value in obj.items():
                if key == 'isUpdate' and value is True:
                    obj[key] = False
                else:
                    update_flag(value)

    update_flag(data)

    with open(file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, Dumper=MyDumper, default_flow_style=False)


if __name__ == '__main__':
    cli()
