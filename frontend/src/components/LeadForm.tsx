// LeadForm Component - Customer facing form
import { useState } from 'react';
import { useForm } from 'react-hook-form';
import Joi from 'joi';
import { joiResolver } from '@hookform/resolvers/joi';
import { Button } from './Button';
import { Input, Select, Checkbox } from './Input';
import { leadApi } from '../services/api';
import { LeadFormData, ProductType, PreferredTime } from '../types';
import { Phone, User, CreditCard, AlertCircle, CheckCircle } from 'lucide-react';

// Validation schema
const leadSchema = Joi.object({
  full_name: Joi.string().min(2).max(100).required().label('Full Name'),
  phone: Joi.string()
    .pattern(/^20\d{9}$/)
    .required()
    .label('Phone Number'),
  lao_id: Joi.string().min(13).max(15).pattern(/^\d+$/).required().label('Lao ID'),
  product: Joi.string()
    .valid(...Object.values(ProductType))
    .required()
    .label('Product Interest'),
  amount: Joi.number()
    .min(1000000)
    .max(500000000)
    .when('product', {
      is: Joi.string().valid(ProductType.PERSONAL_LOAN, ProductType.HOME_LOAN),
      then: Joi.required(),
      otherwise: Joi.optional().allow(null),
    }),
  preferred_time: Joi.string()
    .valid(...Object.values(PreferredTime))
    .optional()
    .label('Preferred Contact Time'),
  consent_given: Joi.boolean().valid(true).required().label('Consent'),
});

interface LeadFormProps {
  onSuccess?: () => void;
}

export function LeadForm({ onSuccess }: LeadFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm<LeadFormData>({
    resolver: joiResolver(leadSchema),
  });

  const selectedProduct = watch('product');

  const onSubmit = async (data: LeadFormData) => {
    setIsSubmitting(true);
    setSubmitError(null);

    try {
      await leadApi.createLead(data);
      setSubmitSuccess(true);
      onSuccess?.();
    } catch (error: any) {
      setSubmitError(
        error.response?.data?.detail || 'Failed to submit. Please try again.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  if (submitSuccess) {
    return (
      <div className="bg-white rounded-2xl shadow-card p-8 max-w-form mx-auto text-center">
        <div className="w-16 h-16 bg-success/10 rounded-full flex items-center justify-center mx-auto mb-4">
          <CheckCircle className="w-8 h-8 text-success" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          ຂໍແກະສຶກສົບຜ່ອນ!
        </h2>
        <p className="text-gray-600 mb-6">
          Thank you! A STBank representative will contact you within 2 business hours.
        </p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-2xl shadow-card p-6 sm:p-8 max-w-form mx-auto">
      {/* Header */}
      <div className="text-center mb-6">
        <h1 className="text-2xl sm:text-3xl font-bold text-primary-500 mb-2">
          ໂຄນເຕື້ອມ 2 ໂມງ
        </h1>
        <p className="text-gray-600">Get a call back in 2 hours</p>
      </div>

      {/* Error Message */}
      {submitError && (
        <div className="mb-6 p-4 bg-error/10 border border-error/20 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-error flex-shrink-0 mt-0.5" />
          <p className="text-sm text-error">{submitError}</p>
        </div>
      )}

      {/* Form */}
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5">
        {/* Full Name */}
        <Input
          label="Full Name / ຊື່ແລະນາມ"
          placeholder="Enter your full name"
          {...register('full_name')}
          error={errors.full_name?.message}
          leftIcon={<User className="w-5 h-5" />}
          required
        />

        {/* Phone Number */}
        <Input
          label="Phone Number / ເບີໂທ"
          placeholder="20XXXXXXXX (9 digits)"
          {...register('phone')}
          error={errors.phone?.message}
          leftIcon={<Phone className="w-5 h-5" />}
          hint="Lao format: 20XXXXXXXX (9 digits after 20)"
          required
        />

        {/* Lao ID */}
        <Input
          label="Lao ID Number / ເລກບັດປະຊາຊົນ"
          placeholder="13-15 digits"
          {...register('lao_id')}
          error={errors.lao_id?.message}
          leftIcon={<CreditCard className="w-5 h-5" />}
          required
        />

        {/* Product Interest */}
        <Select
          label="Product Interest / ເສື້ອມໃກ້ເສດ"
          placeholder="Select a product"
          {...register('product')}
          error={errors.product?.message}
          options={[
            { value: ProductType.SAVINGS_ACCOUNT, label: 'Savings Account / ບັດເກງ' },
            {
              value: ProductType.PERSONAL_LOAN,
              label: 'Personal Loan / ເງີນສົນເສຍ',
            },
            {
              value: ProductType.HOME_LOAN,
              label: 'Home Loan / ເງີນຊ່ອບ້າ',
            },
            {
              value: ProductType.CREDIT_CARD,
              label: 'Credit Card / ບັດເຄເດິ',
            },
          ]}
          required
        />

        {/* Loan Amount (conditional) */}
        {(selectedProduct === ProductType.PERSONAL_LOAN ||
          selectedProduct === ProductType.HOME_LOAN) && (
          <Input
            label="Loan Amount (LAK) / ຈໍາເງີນ"
            type="number"
            placeholder="1,000,000 - 500,000,000"
            {...register('amount', { valueAsNumber: true })}
            error={errors.amount?.message}
            hint="Min: 1,000,000 LAK, Max: 500,000,000 LAK"
          />
        )}

        {/* Preferred Contact Time */}
        <Select
          label="Preferred Contact Time / ເວລາໂທຫາ"
          placeholder="Select preferred time"
          {...register('preferred_time')}
          options={[
            { value: PreferredTime.MORNING, label: 'Morning (8:00 - 12:00)' },
            { value: PreferredTime.AFTERNOON, label: 'Afternoon (13:00 - 17:00)' },
            { value: PreferredTime.EVENING, label: 'Evening (17:00 - 20:00)' },
          ]}
        />

        {/* Consent */}
        <Checkbox
          label="I consent to STBank contacting me regarding financial products."
          {...register('consent_given')}
          error={errors.consent_given?.message}
        />

        {/* Submit Button */}
        <Button
          type="submit"
          className="w-full"
          size="lg"
          isLoading={isSubmitting}
        >
          Submit / ສົ່ງ
        </Button>
      </form>
    </div>
  );
}

export default LeadForm;