import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import LargeFieldGroup from '../components/LargeFieldGroup';
import '@testing-library/jest-dom';

test('renders component', () => {
    const testFields =  {
        age: {
            name: 'Age',
            value: 22,
        },
        gender: {
            name: 'Gender',
            value: 'Male',
        },
        testfield: {
            name: 'Test Field',
            value: 'test value'
        }
    }

    render(<LargeFieldGroup fieldSet={['age', 'gender', 'testfield']} fields={testFields}/>)

    const ageField = screen.getByText('Age');
    const genderField = screen.getByText('Gender')
    const testField = screen.getByText('Test Field')

    expect(ageField).toBeInTheDocument();
    expect(genderField).toBeInTheDocument();
    expect(testField).toBeInTheDocument();

});

// TODO add test that checks that it generates correct size and correct number of boxes?


// Tests to Add---------------------------------------------------------------
//  
//
//