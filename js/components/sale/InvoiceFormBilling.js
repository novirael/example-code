import React, {useState, useEffect} from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { Field } from 'redux-form';
import { Col, Row } from 'react-bootstrap';
import { BooleanField, DecimalField, SelectField, StringField } from '../widgets/fields';

const paymentMethodChoices = [
  {id: '0', name: 'Gotówka'},
  {id: '1', name: 'Przelew Bankowy'},
  {id: '2', name: 'Karta'},
];

const paymentMaturnityChoices = [
  {id: '3', name: '3 dni'},
  {id: '7', name: '7 dni'},
  {id: '14', name: '14 dni'},
  {id: '21', name: '21 dni'},
  {id: '30', name: '30 dni'},
  {id: '60', name: '60 dni'},
  {id: '90', name: '90 dni'},
  {id: '120', name: '120 dni'},
];

function InvoiceFormBilling({changeField}) {
  const [isPaidInAdvance, setIsPaidInAdvance] = useState(false);
  function handleChangeIsFullyPaidInAdvance(value) {
    changeField('payment_maturnity', '');
    changeField('advance_payment', 0);
    setIsPaidInAdvance(value);
  }
  return (
      <div>
          <h3>Rozliczenie</h3>
          <Row>
              <Col>
                  <Field
                      name="is_fully_paid_in_advance"
                      component={BooleanField}
                      label="Zapłacono z góry za fakturę"
                      inline={true}
                      onChangeCallback={handleChangeIsFullyPaidInAdvance}
                  />
              </Col>
          </Row>
          <Row>
              <Col md={2} sm={2}>
                  <Field
                      name="payment_methods"
                      component={SelectField}
                      choices={paymentMethodChoices}
                      label="Sposób płatności"
                      isRequired={true}
                      inline={true}
                  />
              </Col>
              <Col md={2} sm={2}>
                  <Field
                      name="payment_maturnity"
                      component={SelectField}
                      choices={paymentMaturnityChoices}
                      label="Termin płatności"
                      inline={true}
                      readOnly={isPaidInAdvance}
                  />
              </Col>
              <Col md={2} sm={2}>
                  <Field
                      name="advance_payment"
                      component={DecimalField}
                      label="Zapłacono"
                      isRequired={true}
                      inline={true}
                      readOnly={isPaidInAdvance}
                  />
              </Col>
              <Col md={6} sm={6}>
                  <Field
                      name="note"
                      component={StringField}
                      label="Uwagi"
                      isRequired={true}
                      inline={true}
                  />
              </Col>
          </Row>
      </div>
  );
}

InvoiceFormBilling.propTypes = {
  changeField: PropTypes.func.isRequired,
};

export default InvoiceFormBilling;
