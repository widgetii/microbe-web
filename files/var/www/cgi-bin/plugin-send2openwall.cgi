#!/usr/bin/haserl
<%in p/common.cgi %>
<%
plugin="openwall"
plugin_name="Send to OpenWall"
page_title="Send to OpenWall"
params="enabled interval socks5_enabled"

tmp_file=/tmp/${plugin}.conf

config_file="${ui_config_dir}/${plugin}.conf"
[ ! -f "$config_file" ] && touch $config_file

if [ "POST" = "$REQUEST_METHOD" ]; then
  # parse values from parameters
  for _p in $params; do
    eval ${plugin}_${_p}=\$POST_${plugin}_${_p}
    sanitize "${plugin}_${_p}"
  done; unset _p

  ### Validation
  if [ "true" = "$openwall_enabled" ]; then
    [ "$openwall_interval" -lt "15" ] && flash_append "danger" "Keep interval at 15 minutes or longer." && error=11
  fi

  if [ -z "$error" ]; then
    # create temp config file
    :>$tmp_file
    for _p in $params; do
      echo "${plugin}_${_p}=\"$(eval echo \$${plugin}_${_p})\"" >>$tmp_file
    done; unset _p
    mv $tmp_file $config_file

    # Disable/enable cron job
    cp /etc/crontabs/root /tmp/crontabs.tmp
    sed -i /send2openwall\.sh/d /tmp/crontabs.tmp
    [ "true" = "$openwall_enabled" ] &&
      echo "*/${openwall_interval} * * * * /usr/sbin/send2openwall.sh" >>/tmp/crontabs.tmp
    mv /tmp/crontabs.tmp /etc/crontabs/root

    update_caminfo
    redirect_back "success" "${plugin_name} config updated."
  fi

  redirect_to $SCRIPT_NAME
else
  include $config_file

  # Default values
  [ -z "$openwall_interval" ] && openwall_interval="30"
fi
%>
<%in p/header.cgi %>

<div class="alert alert-info">
<p>This plugin allows you to share images from your OpenIPC camera on the <a href="https://openipc.org/open-wall">Open Wall</a>
 page of our website. But that's not all. It's a metrics agent with meaning. The images you share will allow us to determine
 the quality of images from different cameras. We also collect your MAC address, SoC model, sensor model, flash chip size,
 firmware version, and camera uptime to do this.</p>
</div>

<form action="<%= $SCRIPT_NAME %>" method="post">
  <% field_switch "openwall_enabled" "Enable sending to OpenWall" %>
  <div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4 mb-4">
    <div class="col">
      <% field_number "openwall_interval" "Interval, minutes" "15,60,1" "Time between submissions. 15 minutes or longer." %>
      <% field_switch "openwall_socks5_enabled" "Use SOCKS5" "<a href=\"network-socks5.cgi\">Configure</a> SOCKS5 access" %>
      <% button_submit %>
    </div>
  </form>
  <div class="col">
    <% ex "cat $config_file" %>
    <% ex "grep send2openwall /etc/crontabs/root" %>
  </div>
  <div class="col">
    <% preview %>
    <% if [ "true" = "$openwall_enabled" ]; then %>
      <p><a href="send2openwall.cgi" class="btn btn-primary" id="send-to-ftp">Send to OpenWall</a></p>
    <% fi %>
  </div>
</div>

<% [ -f "/tmp/webui/${plugin}.log" ] && link_to "Download log file" "dl.cgi?file=${plugin}.log" %>

<%in p/footer.cgi %>
