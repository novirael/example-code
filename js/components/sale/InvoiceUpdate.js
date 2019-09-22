import React, { useEffect } from 'react';
import { Grid } from 'react-bootstrap';
import Header from '../Header';
import LinksBar from '../LinksBar';

import InvoiceForm from './InvoiceFormContainer';

function InvoiceUpdate({dataFetched, invoiceData, fetchInvoice, fetchInvoiceCustomer, fetchInvoiceReceiver, updateInvoice}) {
    useEffect(fetchInvoice, []);

    if (!dataFetched) {
        return null;
    }

    return (
        <Grid>
            <Header
                title="Faktury"
                subtitle="modyfikuj istniejący dokument"
            />
            <LinksBar
                breadcrumbs={[
                    { label: 'Faktury', ref: '/sale/invoices/' },
                    { label: invoiceData.unique_number || 'unknown', ref: `/sale/invoices/details/${invoiceData.id}/`, legacy: true },
                    { label: 'Modyfikuj', ref: null },
                ]}
            />
            <InvoiceForm
                onSubmit={updateInvoice}
                initialValues={invoiceData}
                editMode={true}
            />
        </Grid>
    )
};

export default InvoiceUpdate;
