# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|

  config.vm.box = "centos64"
  config.vm.box_url = "http://ceph.com/noah/vagrant-centos-6-4.box"

  config.vm.provision :shell, :path => "bootstrap.sh"

  # config.vm.network :forwarded_port, guest: 80, host: 8080
  config.vm.network :public_network, :bridge => 'eth0'

  config.vm.provider "virtualbox" do |v|
    v.customize ["modifyvm", :id, "--memory", "1024"]
    v.customize ["modifyvm", :id, "--cpus", "2"]
  end

end
