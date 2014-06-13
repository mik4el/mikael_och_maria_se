name "mikael_och_maria_se_template"
run_list("recipe[apt::default]",
  "recipe[build-essential::default]",
  "recipe[yum]",
  "recipe[ntp]",
  "recipe[runit]",
  "recipe[ohai]",
  "recipe[openssl]",
  "recipe[python]",
  "recipe[nginx]",
  "recipe[mysql::server]")
 override_attributes "mysql" => { "server_root_password" => "test",
  "server_repl_password" => "test",
  "server_debian_password" => "test",
  "bind_address" => "127.0.0.1"}