-- Remove Companyweb credentials
UPDATE res_company
   SET cweb_login = NULL, cweb_password = NULL;
