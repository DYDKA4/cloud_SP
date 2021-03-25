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
  password    = "102"
  auth_url    = "https://sky.ispras.ru:13000"
  user_domain_name = "ispras"
  project_domain_name = "ispras" 
  region      = "regionOne"
  #  send_service_user_token = True
#  project_name="sandbox"
}

# Create a web server
resource "openstack_compute_instance_v2" "tulin" {
  name            = "ABC"
  image_id        = "Заглушка"
  flavor_name     = "Заглушка"
  key_pair        = "ABC123"
  
  security_groups = ["default"]

  metadata = {
    this = "that"   
  }

  network {
    name = "net-for-83.149.198-sandbox"
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

