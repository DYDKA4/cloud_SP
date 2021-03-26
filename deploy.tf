# Define required providers
terraform {
required_version = ">= 0.14.0"
  required_providers {
    openstack = {
      source  = "terraform-provider-openstack/openstack"
      version = "~> 1.35.0"
    }
  }
}

# Configure the OpenStack Provider
provider "openstack" {
  user_name   = "tulin"
  tenant_name = "sandbox"
  password    = "KfrGtgHbb6"
  auth_url    = "https://sky.ispras.ru:13000"
  user_domain_name = "ispras"
  project_domain_name = "ispras" 
  region      = "regionOne"
  #  send_service_user_token = True
#  project_name="sandbox"
}

# Create a web server
resource "openstack_compute_instance_v2" "tulin" {
  name            = "tulin_network"
  image_id        = "fabulous.cmedium"
  flavor_name     = "81fb0659-81d2-4f3f-a9b2-0c232d4866fe"
  key_pair        = "tulin_key"
  
  security_groups = ["default"]

  metadata = {
    this = "that"   
  }

  network {
    name = "123"
  }
} 

resource "openstack_networking_floatingip_v2" "floating_ip" {
  pool = "external_network"
}
# разобратсья с ${...}
resource "openstack_compute_floatingip_associate_v2" "fip_associate" {
  floating_ip = "${openstack_networking_floatingip_v2.floating_ip.address}"
  instance_id = "${openstack_compute_instance_v2.tulin.id}"
}

