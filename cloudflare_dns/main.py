import os
import click
import CloudFlare
from dotenv import load_dotenv
from CloudFlare.exceptions import CloudFlareAPIError

load_dotenv()


class CloudflareManager:
    def __init__(self, email, api_token):
        self.cf = CloudFlare.CloudFlare(email=email, token=api_token)

    def get_zone_id(self, domain):
        try:
            zones = self.cf.zones.get(params={'name': domain})
            if zones:
                return zones[0]['id']
            return None
        except CloudFlareAPIError as e:
            print(f"Error fetching zone ID: {e}")
            return None

    def get_dns_records(self, zone_id):
        try:
            return self.cf.zones.dns_records.get(zone_id)
        except CloudFlareAPIError as e:
            print(f"Error fetching DNS records: {e}")
            return None

    def create_dns_record(self, zone_id, record_data):
        try:
            return self.cf.zones.dns_records.post(zone_id, data=record_data)
        except CloudFlareAPIError as e:
            print(f"Error creating DNS record: {e}")
            return None

    def update_dns_record(self, zone_id, record_id, record_data):
        try:
            return self.cf.zones.dns_records.put(zone_id, record_id, data=record_data)
        except CloudFlareAPIError as e:
            print(f"Error updating DNS record: {e}")
            return None


def get_default_from_env(var_name, default=None):
    return os.getenv(var_name, default)


@click.group()
@click.option('--email', '-e', default=lambda: get_default_from_env('CF_EMAIL'), help='Email address')
@click.option('--token', '-t', default=lambda: get_default_from_env('CF_TOKEN'), help='CloudFlare Token')
@click.option('--domain', '-d', help='Domain name')
@click.option('--subdomain', '-s', help='Subdomain name')
@click.pass_context
def cli(ctx, email, token, domain, subdomain):
    """A command CloudFlare add get update DNS."""
    ctx.obj = {
        'EMAIL': email,
        'TOKEN': token,
        'DOMAIN': domain,
        'SUBDOMAIN': subdomain
    }


@cli.command()
@click.pass_context
def get_dns(ctx):
    dns_manager = CloudflareManager(email=ctx.obj['EMAIL'], api_token=ctx.obj['TOKEN'])
    zone_id = dns_manager.get_zone_id(ctx.obj['DOMAIN'])
    if zone_id:
        dns_records = dns_manager.get_dns_records(zone_id)
        if dns_records:
            subdomains = [record['name'] for record in dns_records]
            for record in dns_records:
                if record.get("name") == ctx.obj['SUBDOMAIN']:
                    # print(record.get("name"), record.get('id'), record.get('content'))
                    print(
                        f"Subdomain: {record.get('name')},RecordType: {record.get('type')}, Address: {record.get('content')}")
            if ctx.obj['SUBDOMAIN'] not in subdomains:
                print("Subdomain is not a DNS record")
        else:
            print("No DNS records found")
    else:
        print("Zone not found")


def handle_dns_record(ctx, action, dnstype, content, proxied):
    dns_manager = CloudflareManager(email=ctx.obj['EMAIL'], api_token=ctx.obj['TOKEN'])
    zone_id = dns_manager.get_zone_id(ctx.obj['DOMAIN'])
    record_data = {
        'type': dnstype,
        'name': ctx.obj['SUBDOMAIN'],
        'content': content,
        'ttl': 120,
        'proxied': proxied
    }
    print(record_data)
    if zone_id:
        if action == 'create':
            response = dns_manager.create_dns_record(zone_id, record_data)
            print("Created DNS Record:", response)
        elif action == 'update':
            dns_records = dns_manager.get_dns_records(zone_id)
            if dns_records:
                for record in dns_records:
                    if record.get("name") == ctx.obj['SUBDOMAIN']:
                        record_id = record.get('id')
                        response = dns_manager.update_dns_record(zone_id, record_id, record_data)
                        print("Updated DNS Record:", response)
                        break
                else:
                    print("Subdomain is not a DNS record")
            else:
                print("No DNS records found")


@cli.command()
@click.option('--dnstype', help='DNS TYPE exp: A, CNAME, TXT')
@click.option('--content', '-cont', help='DNS resolution address')
@click.option('--proxied/--no-proxied', default=False, help='Whether the DNS record is proxied')
@click.pass_context
def add_dns(ctx, dnstype, content, proxied):
    print(proxied)
    handle_dns_record(ctx, 'create', dnstype, content, proxied)


@cli.command()
@click.option('--dnstype', help='DNS TYPE exp: A, CNAME, TXT')
@click.option('--content', '-cont', help='DNS resolution address')
@click.option('--proxied/--no-proxied', default=False, help='Whether the DNS record is proxied')
@click.pass_context
def update_dns(ctx, dnstype, content, proxied):
    handle_dns_record(ctx, 'update', dnstype, content, proxied)


if __name__ == "__main__":
    cli()
