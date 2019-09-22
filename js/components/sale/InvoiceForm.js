import React, {useState} from 'react';
import PropTypes from 'prop-types';
import { Button, Form, Grid } from 'react-bootstrap';
import { Field } from 'redux-form';
import { BooleanField, StringField } from '../widgets/fields';
import ContractorFields from '../business/ContractorFieldsContainer';
import InvoiceFormPrimary from './InvoiceFormPrimary';
import InvoiceFormBilling from './InvoiceFormBilling';
import InvoiceFormItems from './InvoiceFormItems';

function InvoiceFormContractor({initialValues, changeField}) {
    const [isReceiverDifferent, setIsReceiverDifferent] = useState(!!initialValues.receiverId);
    const [isAuthorizedDifferent, setIsAuthorizedDifferent] = useState(!!initialValues.authorized_to_receive);
    return (
        <div>
            <h3>Nabywca</h3>
            <ContractorFields
                contractorName="customer"
                initialValues={initialValues.customer}
                onSelectedContractor={c => changeField('customer', c)}
            />
            <BooleanField
                label="Odbiorcą faktury jest inny podmiot"
                inline={true}
                input={{
                    value: isReceiverDifferent,
                    onChange: () => setIsReceiverDifferent(!isReceiverDifferent),
                }}
            />
            {isReceiverDifferent && (
                <React.Fragment>
                    <h3>Odbiorca</h3>
                    <ContractorFields
                        contractorName="receiver"
                        initialValues={initialValues.receiver}
                        onSelectedContractor={c => changeField('receiver', c)}
                    />
                </React.Fragment>
            )}
            <BooleanField
                label="Osoba upowaniona do odbioru jest inna niż odbiorca"
                inline={true}
                input={{
                    value: isAuthorizedDifferent,
                    onChange: () => setIsAuthorizedDifferent(!isAuthorizedDifferent),
                }}
            />
            {isAuthorizedDifferent && (
                <Field
                    name="authorized_to_receive"
                    component={StringField}
                    label="Upoważniony(a)"
                    inline={true}
                />
            )}
        </div>
    );
}

function InvoiceFormSubmitButton({submitting, editMode}) {
    const submitLabel = editMode ? 'Modyfikuj fakturę' : 'Utwórz fakturę';
    const submittingLabel = editMode ? 'Modyfikuje fakturę...' : 'Tworzę fakturę...';
    return (
        <Button bsStyle="primary" type="submit" disabled={submitting}>
            {submitting ? submittingLabel : submitLabel}
        </Button>
    );
}

function InvoiceForm({branches, categories, users, handleSubmit, submitting, initialValues, changeField, editMode}) {
    return (
        <Grid>
            <Form horizontal onSubmit={handleSubmit}>
                <InvoiceFormPrimary
                    branches={branches}
                    categories={categories}
                    users={users}
                    numberAssigned={!!initialValues.unique_number}
                />
                <InvoiceFormContractor
                    initialValues={initialValues}
                    changeField={changeField}
                />
                <InvoiceFormBilling
                    changeField={changeField}
                />
                <InvoiceFormItems
                    changeField={changeField}
                />
                <InvoiceFormSubmitButton
                    submitting={submitting}
                    editMode={editMode}
                />
            </Form>
        </Grid>
    );
}

InvoiceForm.propTypes = {
    branches: PropTypes.array.isRequired,
    categories: PropTypes.array.isRequired,
    users: PropTypes.array.isRequired,
    handleSubmit: PropTypes.func.isRequired,
    submitting: PropTypes.bool.isRequired,
    initialValues: PropTypes.object.isRequired,
    changeField: PropTypes.func.isRequired,
    editMode: PropTypes.bool,
};

export default InvoiceForm;
