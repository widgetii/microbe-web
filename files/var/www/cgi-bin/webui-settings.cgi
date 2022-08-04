#!/usr/bin/haserl --upload-limit=100 --upload-dir=/tmp
<%in p/common.cgi %>
<%
locale_file=/etc/webui/locale

if [ "POST" = "$REQUEST_METHOD" ]; then
  case "$POST_action" in
  access)
    new_password="$POST_ui_password"
    [ -z "$new_password" ] && error="Password cannot be empty!"
    [ "$ui_password_fw" = "$new_password" ] && error="You cannot use default password!"
    [ -n "$(echo "$new_password" | grep " ")" ] && error="Password cannot have spaces!"
    [ "5" -ge "${#new_password}" ] && error="Password cannot be shorter than 6 characters!"

    [ -n "$error" ] && redirect_to $SCRIPT_NAME "danger" "$error"

    sed -i s/:admin:.*/:admin:${new_password}/ /etc/httpd.conf
    echo "root:${new_password}" | chpasswd
    update_caminfo
    redirect_to "/" "success" "Password updated."
    ;;

  locale)
    locale="$POST_ui_language" # set language.
    # upload new language and switch to it. overrides aboveset language.
    _fname="$POST_ui_locale_file_name"
    if [ -n "$_fname" ]; then
      mv "$POST_ui_locale_file_path" /var/www/lang/$_fname
      locale=${_fname%%.*}
    fi
    # save new language settings and reload locale
    [ -z "$locale" ] && locale="en"
    echo "$locale" >$locale_file
    reload_locale
    update_caminfo
    redirect_to $SCRIPT_NAME "success" "Locale updated."
    ;;

  *)
    redirect_to $SCRIPT_NAME "danger" "UNKNOWN ACTION: $POST_action"
    ;;
  esac
fi

page_title="Web Interface Settings"

# data for form fields
ui_username="admin"
ui_language="$locale"

ui_locales="en|English"
if [ -d /var/www/lang/ ]; then
 for i in $(ls -1 /var/www/lang/); do
    code="$(basename $i)"; code="${code%%.sh}"
    name="$(sed -n 2p $i|sed "s/ /_/g"|cut -d: -f2)"
    ui_locales="${ui_locales},${code}|${name}"
  done
fi
%>
<%in p/header.cgi %>

<div class="row row-cols-1 row-cols-md-2 row-cols-lg-3 g-4 mb-4">
  <div class="col">
    <h3>Access</h3>
    <form action="<%= $SCRIPT_NAME %>" method="post">
      <% field_hidden "action" "access" %>
      <p class="string">
        <label for="ui_username" class="form-label">Username</label>
        <input type="text" id="ui_username" name="ui_username" value="admin" class="form-control" autocomplete="username" disabled>
      </p>
      <% field_password "ui_password" "Password" %>
      <% # field_password "webui_password_confirmation" "Confirm Password" %>
      <% button_submit %>
    </form>
  </div>
  <div class="col">
    <h3>Locale</h3>
    <form action="<%= $SCRIPT_NAME %>" method="post" enctype="multipart/form-data">
      <% field_hidden "action" "locale" %>
      <% field_select "ui_language" "Interface Language" "$ui_locales" %>
      <%# field_file "ui_locale_file" "Locale file" %>
      <% button_submit %>
    </form>
  </div>

<% if [ "$debug" -ge "1" ]; then %>
  <div class="col">
    <h3>Configuration</h3>
    <%
    ex "cat /etc/httpd.conf"
    #ex "echo \$locale"
    #ex "cat $locale_file"
    #ex "ls /var/www/lang/"
    %>
  </div>
<% fi %>
</div>

<%in p/footer.cgi %>
