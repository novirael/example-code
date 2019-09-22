import React, {useEffect} from 'react';
import PropTypes from 'prop-types';
import { Field } from 'redux-form';
import { Button, ButtonGroup, Col, Glyphicon, Row } from 'react-bootstrap';
import { DecimalField, SelectField, StringField } from '../widgets/fields';

const taxChoices = [
  {id: '.23', name: '23%'},
  {id: '.08', name: '8%'},
  {id: '.00', name: '-'},
];

const measureChoices = [
  {id: 'szt', name: 'sztuka'},
  {id: 'usl', name: 'usługa'},
  {id: 'para', name: 'para'},
  {id: 'tona', name: 'tona'},
  {id: 'km', name: 'kilometr'},
  {id: 'm2', name: 'metr kwadratowy'},
  {id: 'm3', name: 'metr szescienny'},
];

const decimal = (value) => Math.round(value * 100) / 100;

function InvoiceFormItem({namePrefix, values, changeField, onAddItem, onRemoveItem}) {
  function handleChangeItem(item) {
      changeField(`${namePrefix}.single_price`, item.price || 0);
  }

  useEffect(() => {
      const singlePriceWithTax = decimal(values.single_price * (Number(values.vat) + 1));
      const totalPrice = decimal(singlePriceWithTax * values.quantity);
      changeField(`${namePrefix}.value_vat`, totalPrice);
  }, [values.single_price, values.vat, values.quantity]);

  return (
      <Row>
          <Col md={5} sm={4}>
              <Field
                  name={`${namePrefix}.item`}
                  component={SelectField}
                  label="Produkt lub usługa"
                  choices="inventory-items"
                  isRequired={true}
                  isCreatable={true}
                  inline={true}
                  onChangeCallback={handleChangeItem}
              />
          </Col>
          <Col md={1} smHidden={true}>
              <Field
                  name={`${namePrefix}.pkwiu`}
                  component={StringField}
                  label="PKWiU"
                  inline={true}
              />
          </Col>
          <Col md={1} sm={2}>
              <Field
                  name={`${namePrefix}.single_price`}
                  component={DecimalField}
                  label="Cena netto"
                  isRequired={true}
                  inline={true}
              />
          </Col>
          <Col md={1} sm={2}>
              <Field
                  name={`${namePrefix}.vat`}
                  component={SelectField}
                  choices={taxChoices}
                  label="VAT"
                  isRequired={true}
                  inline={true}
              />
          </Col>
          <Col md={1} sm={1}>
              <Field
                  name={`${namePrefix}.quantity`}
                  component={DecimalField}
                  label="Ilość"
                  isRequired={true}
                  inline={true}
              />
          </Col>
          <Col md={1} smHidden={true}>
              <Field
                  name={`${namePrefix}.measure`}
                  component={SelectField}
                  choices={measureChoices}
                  label="j.m."
                  isRequired={true}
                  inline={true}
              />
          </Col>
          <Col md={1} sm={2}>
              <Field
                  name={`${namePrefix}.value_vat`}
                  component={DecimalField}
                  label="Wartość brutto"
                  isRequired={true}
                  inline={true}
              />
          </Col>
          <Col md={1} sm={1}>
              <ButtonGroup className="invoice-item-actions">
                  <Button onClick={onAddItem}>
                      <Glyphicon glyph="plus" />
                  </Button>
                  <Button onClick={onRemoveItem}>
                      <Glyphicon glyph="minus" />
                  </Button>
              </ButtonGroup>
          </Col>
      </Row>
  );
}

InvoiceFormItem.propTypes = {
  namePrefix: PropTypes.string.isRequired,
  values: PropTypes.object.isRequired,
  changeField: PropTypes.func.isRequired,
  onAddItem: PropTypes.func.isRequired,
  onRemoveItem: PropTypes.func.isRequired,
};

export default InvoiceFormItem;
