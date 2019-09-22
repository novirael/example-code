import React from 'react';
import PropTypes from 'prop-types';
import { connect } from 'react-redux';
import { FieldArray } from 'redux-form';
import { Col, Row } from 'react-bootstrap';
import { DecimalField } from '../widgets/fields';
import { initialValuesItem } from './InvoiceFormContainer';
import InvoiceFormItem from './InvoiceFormItem';

const decimal = (value) => Math.round(value * 100) / 100;

function InvoiceFormItemsArray({fields, changeField, invoiceItemValues}) {
  return fields.map((fieldName, index) => (
      <InvoiceFormItem
          key={`invoice-row-${fieldName}-${index}`}
          values={invoiceItemValues[index]}
          namePrefix={fieldName}
          changeField={changeField}
          onAddItem={() => fields.splice(index + 1, 0, {...initialValuesItem})}
          onRemoveItem={() => fields.remove(index)}
      />
  ));
}

function InvoiceFormItems({changeField, invoiceItemValues}) {
  return (
      <div>
          <h3>Produkty i usługi</h3>
          <FieldArray
              name="items"
              component={InvoiceFormItemsArray}
              changeField={changeField}
              invoiceItemValues={invoiceItemValues}
          />
          <Row>
              <Col>
                  <DecimalField
                      label="Suma"
                      readOnly={true}
                      input={{
                          value: decimal(
                            invoiceItemValues
                              .map(item => Number(item.value_vat))
                              .reduce((a, b) => a + b, 0)
                          ),
                      }}
                  />
              </Col>
          </Row>
      </div>
  );
}

InvoiceFormItems.propTypes = {
  changeField: PropTypes.func.isRequired,
  invoiceItemValues: PropTypes.array.isRequired,
};

const mapStateToProps = (state) => ({
  invoiceItemValues: state.form.invoiceForm.values.items,
});

export default connect(mapStateToProps)(InvoiceFormItems);