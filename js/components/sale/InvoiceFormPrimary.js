import React from 'react';
import PropTypes from 'prop-types';
import { Field } from 'redux-form';
import { Col, Row } from 'react-bootstrap';
import { DateField, SelectField, } from '../widgets/fields';

function InvoiceFormPrimary({branches, categories, users, numberAssigned}) {
    return (
        <div>
            <h3>Podstawowe informacje</h3>
            <Row>
                <Col md={4} sm={4}>
                    <Field
                        name="branch"
                        component={SelectField}
                        choices={branches}
                        label="Biuro"
                        isRequired={true}
                        readOnly={numberAssigned}
                        inline={true}
                    />
                </Col>
                <Col md={4} sm={4}>
                    <Field
                        name="category"
                        component={SelectField}
                        choices={categories}
                        label="Kategoria"
                        isRequired={true}
                        readOnly={numberAssigned}
                        inline={true}
                    />
                </Col>
                <Col md={4} sm={4}>
                    <Field
                        name="who"
                        component={SelectField}
                        choices={users}
                        label="Osoba wystawiająca"
                        isRequired={true}
                        inline={true}
                    />
                </Col>
            </Row>
            <Row>
                <Col md={6} sm={6}>
                    <Field
                        name="date"
                        component={DateField}
                        label="Data wystawienia"
                        isRequired={true}
                        inline={true}
                    />
                </Col>
                <Col md={6} sm={6}>
                    <Field
                        name="date_of_sale"
                        component={DateField}
                        label="Data sprzeday"
                        isRequired={true}
                        inline={true}
                    />
                </Col>
            </Row>
        </div>
    );
}

InvoiceFormPrimary.propTypes = {
  branches: PropTypes.array.isRequired,
  categories: PropTypes.array.isRequired,
  users: PropTypes.array.isRequired,
};

export default InvoiceFormPrimary;
