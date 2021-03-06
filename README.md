### EVoting App

if hmac expected bytes error:
https://github.com/pallets/itsdangerous/issues/41#issuecomment-69416785

errors:

- If the name of your WTF Form field is 'name' doing {{ name() }} will result in a '...not callable erorr' because each form field has a name attribute which is the name of the field gan. So instead just do this:
  `{{ form['name'](class='class-name') }}`

- if you are rendering FieldLists by yourself, don't forget to include a csrf_token tag for each field entry
  e.g `{{ field.csrf_token }}`

- if you want to pass attributes with hyphens like 'data-name' to a wtform field do:
  `{{ form.field(class='style', **{'data-name': 'value'}) }}`
