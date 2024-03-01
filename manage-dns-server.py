
from support import logger, from_json, validate_json_schema;
import os;
import sys;
import jinja2;

class manage_dns_server:
    def __init__(self):
        self.dns_records = from_json(path="config/dns-records.json");
        self.prepare_and_replace_dns_configuration_local();

    def prepare_and_replace_dns_configuration_local(self):
        logger.info("Prepare and replace the DNS configuration file \"/etc/bind/named.conf.local\".");
        self.render_and_replace_system_files("template/named.conf.local", "/etc/bind/named.conf.local", dns_records=self.dns_records);
        self.prepare_and_replace_dns_zones();

    def prepare_and_replace_dns_zones(self):
        if not os.path.isdir("/etc/bind/zones"):
            os.system("mkdir --parents /etc/bind/zones");
        for config in self.dns_records:
            logger.info(f"Prepare and replace the DNS zones file \"/etc/bind/zones/{config['zone']}\".");
            self.render_and_replace_system_files("template/db.local", f"/etc/bind/zones/{config['zone']}", config=config);
        self.restart_dns_service();

    def render_and_replace_system_files(self, template, path, **kargs):
        if os.path.exists(template):
            with open(template, "r") as file:
                template = jinja2.Template(file.read());
            if os.path.exists(path):
                os.system(f"cp {path} {path}_$(date +'%Y%m%d_%H%M%S')");
            with open(path, "w") as file:
                file.write(template.render(**kargs));
        else:
            logger.critical("The template doesn't exist for the DNS configuration file \"{path}\".");
            sys.exit(1);

    def restart_dns_service(self):
        logger.info("Restart the DNS service and validate.");
        os.system("sudo systemctl restart bind9");

def main():
    validate_json_schema("config/dns-records.json", "schema/dns-records-schema.json");
    manage_dns_server();

if "__main__" in __name__:
    if os.geteuid() != 0:
        logger.critical("Please execute a script with root privileges.");
    else:
        if os.path.isfile("requirements.txt"):
            logger.info("Download the required libraries and install them on the system.");
            os.system("pip install -r requirements.txt");
        main();