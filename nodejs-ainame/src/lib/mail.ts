import nodemailer from 'nodemailer';
import { config } from '../config';

function createTransporter() {
  return nodemailer.createTransport({
    host: config.mail.server,
    port: config.mail.port,
    secure: config.mail.sslTls,
    auth: {
      user: config.mail.username,
      pass: config.mail.password,
    },
    tls: {
      rejectUnauthorized: false,
    },
  });
}

export interface SendMailOptions {
  to: string;
  subject: string;
  text: string;
  html?: string;
}

export async function sendMail(options: SendMailOptions): Promise<void> {
  const transporter = createTransporter();
  await transporter.sendMail({
    from: `"${config.mail.fromName}" <${config.mail.from}>`,
    to: options.to,
    subject: options.subject,
    text: options.text,
    html: options.html,
  });
}
